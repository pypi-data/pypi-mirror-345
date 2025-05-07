#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import json
import sys
import time

import aiohttp
from cache import cache
from env_config import api_config
from fastapi import HTTPException
from livekit import api
from loguru import logger
from rag.weaviate_script import get_weaviate_client
from utils.api_calls import update_webcall_status
from utils.callbacks import end_callback, warning_callback
from utils.frames_monitor import BotSpeakingFrameMonitor
from utils.generic_functions.cleanup import cleanup_connection
from utils.generic_functions.common import (
    convert_tools_for_llm_provider,
    get_vad_params,
)
from utils.generic_functions.response_handler import response_formatters
from utils.llm import initialize_llm_service
from utils.llm_functions.end_call_handler import end_call_function
from utils.llm_functions.generic_function import generic_function_handler
from utils.llm_functions.query_kb import query_knowledge_base
from utils.pipeline import (
    initialize_filler_config,
    initialize_stt_mute_strategy,
    initialize_user_idle,
)
from utils.stt import initialize_stt_service
from utils.tools import base_tools, rag_tool
from utils.transcript import TranscriptHandler
from utils.tts import format_tts_text, initialize_tts_service

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import (
    BotInterruptionFrame,
    TextFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.transcript_processor import TranscriptProcessor
from pipecat.transports.services.livekit import LiveKitParams, LiveKitTransport

# logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


def generate_token_with_agent(
    room_name: str, participant_name: str, api_key: str, api_secret: str
) -> str:
    token = api.AccessToken(api_key, api_secret)
    token.with_identity(participant_name).with_name(participant_name).with_grants(
        api.VideoGrants(
            room_join=True,
            room=room_name,
            agent=True,  # This is the only difference, this makes livekit client know agent has joined
        )
    )

    return token.to_jwt()


async def configure_livekit(room_name):
    url = api_config.LIVEKIT_URL
    api_key = api_config.LIVEKIT_API_KEY
    api_secret = api_config.LIVEKIT_API_SECRET

    if not room_name:
        raise Exception("No LiveKit room specified.")

    if not url:
        raise Exception("No LiveKit server URL specified.")

    if not api_key or not api_secret:
        raise Exception(
            "LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in environment variables."
        )

    token = generate_token_with_agent(room_name, "bot", api_key, api_secret)

    return url, token


async def run_webcall_bot(call_id, call_config, update_call_status_url):
    room_name = call_config["room_name"]
    llm_model = "gpt-4o-mini"
    llm_provider = "openai"  # Added llm_provider to config Groq
    tts_provider = "azure"
    voicemail_detect = False
    call_hold_config = {"detect": False, "end_count": 3}
    tts_voice = "en-US-SaraNeural"
    intro_message = "Hi there!"
    language = "en-IN"
    prompt = "You are a helpful LLM in an audio call. Your goal is to demonstrate your capabilities in a succinct way. Your output will be converted to audio so don't include special characters in your answers. Respond to what the user said in a creative and helpful way. When you feel the conversation has reached a natural conclusion, you can use the end_call function to end the call."
    stt_provider = "azure"
    mute_during_intro = False
    mute_while_bot_speaking = False
    advanced_vad = True
    telephony_provider = "plivo"
    collection_name = api_config.WEAVIATE_COLLECTION_NAME
    kb_name_to_id_map = {}
    idle_timeout_warning = 5
    idle_timeout_end = 10
    pre_query_phrases = [
        "Let me check this for you",
        "Give me a second to look this up",
        "Hang on, I'm checking for that!",
        "Give me a moment to find that information!",
    ]
    record_locally = False
    function_call_monitor = list()
    if call_config:
        logger.debug("Overrriding values", call_config)
        pre_query_phrases = call_config.get("pre_query_response_phrases", pre_query_phrases)
        llm_model = call_config.get("llm_model", llm_model)
        llm_provider = call_config.get(
            "llm_provider", llm_provider
        )  # Getting llm_provider from config
        tts_provider = call_config.get("tts_provider", tts_provider)
        tts_voice = call_config.get("voice", tts_voice)
        intro_message = call_config.get("intro_message") or intro_message

        kb_name_to_id_map = call_config.get("kb_name_to_id_map", kb_name_to_id_map)
        collection_name = call_config.get("collection_name", collection_name)
        voicemail_detect = call_config.get("voicemail_detect", voicemail_detect)
        call_hold_config = call_config.get("call_hold_config", call_hold_config)
        prompt = call_config.get("prompt", prompt)
        prompt += "\nNote: Today's date is : " + time.strftime("%d %B,%Y and day is %A.")

        if call_config.get("use_rag", False):
            prompt += "\nTo retrieve information using the knowledgebase invoke the function query_knowledge_base with user query and the name of the knowledgebase."
            # connect to weaviate
            weaviate_client = get_weaviate_client()
            await weaviate_client.connect()

        language = call_config.get("language", language)
        stt_provider = call_config.get("stt_provider", stt_provider)
        mute_during_intro = call_config.get("mute_during_intro", mute_during_intro)
        mute_while_bot_speaking = call_config.get(
            "mute_while_bot_speaking", mute_while_bot_speaking
        )
        idle_timeout_warning = call_config.get("idle_timeout_warning", idle_timeout_warning)
        idle_timeout_end = call_config.get("idle_timeout_end", idle_timeout_end)
        if language.lower() == "hi-in":
            language = "hi"
        advanced_vad = call_config.get("advanced_vad", advanced_vad)
        telephony_provider = call_config.get("telephony_provider", telephony_provider)

    # Create the final_message_done_event for synchronization
    final_message_done_event = asyncio.Event()
    vad_params_speaking, vad_params_bot_silent = get_vad_params(advanced_vad)
    bot_speaking_frame_monitor = BotSpeakingFrameMonitor(
        final_message_done_event, vad_params_bot_silent, vad_params_speaking
    )

    (url, token) = await configure_livekit(room_name)

    # Create transcript processor and handler
    transcript = TranscriptProcessor()
    transcript_handler = TranscriptHandler(logger)

    # initialize the transcript
    transport = LiveKitTransport(
        url=url,
        token=token,
        room_name=room_name,
        params=LiveKitParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            camera_out_enabled=False,
            vad_analyzer=SileroVADAnalyzer(),
            vad_enabled=True,
            vad_audio_passthrough=True,
        ),
    )
    llm = initialize_llm_service(llm_provider=llm_provider, llm_model=llm_model)
    stt = initialize_stt_service(stt_provider=stt_provider, language=language, logger=logger)
    tts = initialize_tts_service(
        tts_provider=tts_provider,
        language=language,
        voice=tts_voice,
        text_formatter=lambda text: format_tts_text(text, language),
        azure_api_key=api_config.AZURE_SPEECH_API_KEY,
        azure_region=api_config.AZURE_SPEECH_REGION,
        elevenlabs_api_key=api_config.ELEVENLABS_API_KEY,
        google_credentials_path="creds.json",
        deepgram_api_key=api_config.DEEPGRAM_API_KEY,
        cartesia_api_key=api_config.CARTESIA_API_KEY,
        tts_model=call_config.get(
            "tts_model", "sonic-2" if tts_provider == "cartesia" else "eleven_turbo_v2_5"
        ),
    )

    task_references = []

    # register functions to llm
    llm.register_function(
        "end_call",
        lambda fn, tool_call_id, args, llm, context, result_callback: end_call_function(
            fn,
            tool_call_id,
            args,
            llm,
            telephony_provider,
            call_id,
            None,
            None,
            call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            bot_speaking_frame_monitor,
            final_message_done_event,
            function_call_monitor,
            logger,
            transport,
        ),
    )

    if call_config and call_config.get("use_rag", False):
        print("registered function")
        llm.register_function(
            "query_knowledge_base",
            lambda fn, tool_call_id, args, llm, context, result_callback: query_knowledge_base(
                fn,
                tool_call_id,
                args,
                tts,
                pre_query_phrases,
                kb_name_to_id_map,
                weaviate_client,
                collection_name,
                result_callback,
                function_call_monitor,
                logger,
            ),
        )
        base_tools.append(rag_tool)

    if call_config and call_config.get("tools"):
        for tool in call_config.get("tools"):
            if tool["name"] != "end_call":  # Avoid duplicate registration
                llm.register_function(
                    tool["name"],
                    lambda fn,
                    tool_call_id,
                    args,
                    llm,
                    context,
                    result_callback: generic_function_handler(
                        fn,
                        tool_call_id,
                        args,
                        llm,
                        call_config,
                        tts,
                        pre_query_phrases,
                        result_callback,
                        cache,
                        response_formatters,
                        function_call_monitor,
                        logger,
                    ),
                )
                base_tools.append(tool)

    tools = convert_tools_for_llm_provider(base_tools, llm_provider)

    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {"role": "assistant", "content": intro_message},
    ]

    context = OpenAILLMContext(messages, tools)
    # Add call_id and stream_id to context for end_call function
    context.call_id = call_id
    context_aggregator = llm.create_context_aggregator(context)

    pipeline_steps = [
        transport.input(),
    ]

    initialize_stt_mute_strategy(mute_during_intro, mute_while_bot_speaking, pipeline_steps)

    # add stt to the pipeline after the mute strategy
    pipeline_steps.extend(
        [
            stt,
        ]
    )
    initialize_filler_config(call_config, transport, tts_voice, language, pipeline_steps)
    user_idle = initialize_user_idle(
        idle_timeout_warning,
        idle_timeout_end,
        lambda idle_proc: end_callback(
            idle_proc,
            telephony_provider,
            call_id,
            None,
            None,
            call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            function_call_monitor,
            logger,
            transport,
            record_locally,
        ),
        lambda idle_proc: warning_callback(
            idle_proc, user_idle, context, function_call_monitor, logger
        ),
    )

    pipeline_steps.extend(
        [
            transcript.user(),
            user_idle,
            context_aggregator.user(),
            llm,  # LLM
            tts,  # Text-To-Speech
            bot_speaking_frame_monitor,  # Add BotSpeakingFrameMonitor here
            transport.output(),  # Websocket output to client
            transcript.assistant(),
            context_aggregator.assistant(),
        ]
    )

    pipeline = Pipeline(pipeline_steps)
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True, enable_metrics=True, enable_usage_metrics=True
        ),
    )

    # Register an event handler so we can play the audio when the
    # participant joins.
    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant_id):
        await asyncio.sleep(1)
        await task.queue_frame(TextFrame(intro_message))

    # Register an event handler to receive data from the participant via text chat
    # in the LiveKit room. This will be used to as transcription frames and
    # interrupt the bot and pass it to llm for processing and
    # then pass back to the participant as audio output.
    @transport.event_handler("on_data_received")
    async def on_data_received(transport, data, participant_id):
        logger.info(f"Received data from participant {participant_id}: {data}")
        # convert data from bytes to string
        json_data = json.loads(data)

        await task.queue_frames(
            [
                BotInterruptionFrame(),
                UserStartedSpeakingFrame(),
                TranscriptionFrame(
                    user_id=participant_id,
                    timestamp=json_data["timestamp"],
                    text=json_data["message"],
                ),
                UserStoppedSpeakingFrame(),
            ],
        )

    @transcript.event_handler("on_transcript_update")
    async def on_transcript_update(processor, frame):
        await transcript_handler.on_transcript_update(processor, frame)

    @transport.event_handler("on_call_state_updated")
    async def on_call_state_updated(transport, state):
        logger.info(f"here is the call state", {state})

    @transport.event_handler("on_participant_disconnected")
    async def on_participant_disconnected(transport, participant_id: str):
        logger.info("here is the participant id", participant_id)
        if call_config and call_config.get("user_rag", False):
            await weaviate_client.close()

        await update_webcall_status(
            call_id=call_id,
            callback_call_id=call_id,
            status="completed",
            sub_status="user_left",
            logger=logger,
        )

        await transport.cleanup()
        await cleanup_connection(
            call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            function_call_monitor,
            logger,
            record_locally,
        )

    @transport.event_handler("on_disconnected")
    async def on_disconnected(transport):
        # logger.info(f"Received data from participant {participant_id}: {data}")
        if call_config and call_config.get("user_rag", False):
            await weaviate_client.close()

        await update_webcall_status(
            call_id=call_id,
            callback_call_id=call_id,
            status="failed",
            sub_status="user_did_not_join",
            logger=logger,
        )

        # await transport.cleanup()
        await cleanup_connection(
            call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            function_call_monitor,
            logger,
            record_locally,
        )

    # make call to backend to clear the data

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)
