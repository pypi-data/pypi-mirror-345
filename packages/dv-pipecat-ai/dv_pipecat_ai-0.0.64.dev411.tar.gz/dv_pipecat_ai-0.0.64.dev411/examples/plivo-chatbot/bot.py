"""Plivo Chatbot Implementation.

This module sets up and runs the Plivo chatbot using various services and processors
from the Pipecat framework.
"""

# Standard Library Imports
import asyncio
import time

# Third-Party Imports
from cache import cache
from dotenv import load_dotenv
from env_config import api_config
from loguru import logger
from rag.weaviate_script import get_weaviate_client
from starlette.websockets import WebSocket
from utils.callbacks import end_callback, warning_callback
from utils.frames_monitor import BotSpeakingFrameMonitor
from utils.generic_functions.cleanup import cleanup_connection
from utils.generic_functions.common import (
    convert_tools_for_llm_provider,
    get_vad_params,
    tool_json_to_function_schema,
)
from utils.generic_functions.response_handler import response_formatters
from utils.llm import initialize_llm_service
from utils.llm_functions.call_transfer import call_transfer_handler, call_transfer_tool
from utils.llm_functions.dtmf_output import dtmf_output_handler, dtmf_output_tool  # Import DTMF
from utils.llm_functions.end_call_handler import end_call_function
from utils.llm_functions.generic_function import generic_function_handler
from utils.llm_functions.query_kb import query_knowledge_base
from utils.llm_functions.switch_language import switch_language_handler, switch_language_tool
from utils.pipeline import (
    initialize_filler_config,
    initialize_hold_detector,
    initialize_stt_mute_strategy,
    initialize_user_idle,
    initialize_voicemail_detector,
    initialise_dtmf_input,
)
from utils.stt import initialize_stt_service
from utils.tools import base_tools, rag_tool
from utils.transcript import TranscriptHandler, save_audio_to_file
from utils.tts import format_tts_text, initialize_tts_service

from pipecat.adapters.schemas.tools_schema import ToolsSchema

# from pipecat.transcriptions.language import Language # Moved to switch_language.py
from pipecat.audio.vad.silero import SileroVADAnalyzer

# First-Party Imports
from pipecat.frames.frames import (
    BotStoppedSpeakingFrame,
    Frame,
    STTUpdateSettingsFrame,  # Keep this if needed elsewhere, or remove if only for switch_language
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
)
from pipecat.processors.audio.audio_buffer_processor import AudioBufferProcessor
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

# Local Application Imports
from pipecat.processors.transcript_processor import TranscriptProcessor
from pipecat.serializers.exotel import ExotelFrameSerializer
from pipecat.serializers.plivo import PlivoFrameSerializer
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

# Initialize Environment Variables
load_dotenv(override=True)

# sentry_sdk.init(
#     dsn=os.getenv("SENTRY_DSN"),
#     server_name=get_hostname(),
#     environment=os.getenv("ENVIRONMENT"),
#     sample_rate=0.5,
# )

# logger.remove(0)
# logger.add(sys.stderr, level="DEBUG")


# Define TTSCompletionListener
class TTSCompletionListener(FrameProcessor):
    def __init__(self, tts_done_event, **kwargs):
        super().__init__(**kwargs)
        self.tts_done_event = tts_done_event
        self.waiting_for_final_tts = False  # Initialize the flag

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await self.push_frame(frame, direction)
        if self.waiting_for_final_tts and isinstance(frame, BotStoppedSpeakingFrame):
            self.tts_done_event.set()
            self.waiting_for_final_tts = False  # Reset the flag


def get_telephony_serialiser(provider, stream_id):
    if provider == "plivo":
        return PlivoFrameSerializer(stream_id=stream_id)
    elif provider == "exotel":
        return ExotelFrameSerializer(stream_sid=stream_id)
    elif provider == "custom":
        return ExotelFrameSerializer(stream_sid=stream_id)


# Define BotSpeakingFrameMonitor


async def run_bot(
    websocket_client: WebSocket, call_id, stream_id, callback_call_id, call_config=None
):
    bot_logger = logger.bind(call_id=callback_call_id or call_id)
    bot_logger.info(f"Call config: {call_config}")
    # Default configurations
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
    vocab = []  # Default to empty list
    idle_timeout_warning = 5
    idle_timeout_end = 10
    pre_query_phrases = [
        "Let me check this for you",
        "Give me a second to look this up",
        "Hang on, I'm checking for that!",
        "Give me a moment to find that information!",
    ]
    record_locally = False
    # Override defaults with call_config if provided

    function_call_monitor = list()

    if call_config:
        bot_logger.debug("Overrriding values", call_config)
        pre_query_phrases = call_config.get("pre_query_response_phrases", pre_query_phrases)
        llm_model = call_config.get("llm_model", llm_model)
        llm_provider = call_config.get(
            "llm_provider", llm_provider
        )  # Getting llm_provider from config
        tts_provider = call_config.get("tts_provider", tts_provider)
        tts_voice = call_config.get("voice", tts_voice)
        intro_message = call_config.get("intro_message") or intro_message

        # Check if we should record locally instead of using Plivo's recording
        record_locally = call_config.get("record", False)
        audio_buffer = None

        kb_name_to_id_map = call_config.get("kb_name_to_id_map", kb_name_to_id_map)
        collection_name = call_config.get("collection_name", collection_name)
        voicemail_detect = call_config.get("voicemail_detect", voicemail_detect)
        call_hold_config = call_config.get("call_hold_config", call_hold_config)
        prompt = call_config.get("prompt", prompt)
        prompt += "\nNote: Today's date is : " + time.strftime("%d %B,%Y and day is %A.")

        # Create audio processor if we're recording locally
        if record_locally:
            audio_buffer = AudioBufferProcessor(
                sample_rate=8000,
                num_channels=1,  # Mono
                buffer_size=0,  # Only trigger at end of recording
                user_continuous_stream=False,
            )

            # Register event handler
            @audio_buffer.event_handler("on_audio_data")
            async def on_audio_data(buffer, audio, sample_rate, num_channels):
                await save_audio_to_file(
                    audio, sample_rate, num_channels, callback_call_id or call_id
                )

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
        vad_input = call_config.get("vad_input")
        vocab = call_config.get("vocab", [])  # Get vocab list, default to empty if not present

    # Create the final_message_done_event for synchronization
    final_message_done_event = asyncio.Event()
    vad_params_speaking, vad_params_bot_silent = get_vad_params(advanced_vad, vad_input)
    bot_speaking_frame_monitor = BotSpeakingFrameMonitor(
        final_message_done_event, vad_params_bot_silent, vad_params_speaking
    )

    # Create transcript processor and handler
    transcript = TranscriptProcessor()
    transcript_handler = TranscriptHandler(bot_logger)

    transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_out_enabled=True,
            add_wav_header=False,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            vad_audio_passthrough=True,
            serializer=get_telephony_serialiser(telephony_provider, stream_id),
            # audio_out_sample_rate=16000 if tts_provider == "elevenlabs" else 24000,
            # audio_in_filter=NoisereduceFilter(),
        ),
    )

    llm = initialize_llm_service(llm_provider=llm_provider, llm_model=llm_model)

    # In the run_bot function, before defining end_call_function
    task_references = []

    # --- Expert Tool Registration and Appending ---
    # Build a list of (tool_dict, tool_name, handler_func or None) tuples
    tool_candidates = []
    dedup_names = set()

    # Base tool(s)
    for t in base_tools:
        tool_candidates.append((t, t["name"], "end_call" if t["name"] == "end_call" else None))
        dedup_names.add(t["name"])

    # RAG tool
    if call_config and call_config.get("use_rag", False):
        tool_candidates.append((rag_tool, rag_tool["name"], "query_knowledge_base"))
        dedup_names.add(rag_tool["name"])

    # Switch language tool
    if "switch_language" in prompt:
        tool_candidates.append(
            (switch_language_tool, switch_language_tool["name"], "switch_language")
        )
        dedup_names.add(switch_language_tool["name"])

    # Call transfer tool
    if "call_transfer" in prompt:
        tool_candidates.append((call_transfer_tool, call_transfer_tool["name"], "call_transfer"))
        dedup_names.add(call_transfer_tool["name"])

    # DTMF output tool
    if "dtmf_output" in prompt:
        tool_candidates.append((dtmf_output_tool, dtmf_output_tool["name"], "dtmf_output"))
        dedup_names.add(dtmf_output_tool["name"])

    # Custom tools from call_config
    if call_config and call_config.get("tools"):
        for tool in call_config["tools"]:
            if tool["name"] not in dedup_names:
                tool_candidates.append((tool, tool["name"], "generic_function"))
                dedup_names.add(tool["name"])

    # Handler mapping
    handler_map = {
        "end_call": lambda fn, tool_call_id, args, llm, context, result_callback: end_call_function(
            fn,
            tool_call_id,
            args,
            llm,
            telephony_provider,
            call_id,
            stream_id,
            websocket_client,
            callback_call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            bot_speaking_frame_monitor,
            final_message_done_event,
            function_call_monitor,
            bot_logger,
            None,
        ),
        "query_knowledge_base": lambda fn,
        tool_call_id,
        args,
        llm,
        context,
        result_callback: query_knowledge_base(
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
            bot_logger,
        ),
        "switch_language": lambda fn,
        tool_call_id,
        args,
        llm_svc,
        context,
        result_callback: switch_language_handler(
            fn, tool_call_id, args, llm_svc, context, result_callback, bot_logger
        ),
        "call_transfer": lambda fn,
        tool_call_id,
        args,
        llm_svc,
        context,
        result_callback: call_transfer_handler(
            fn,
            tool_call_id,
            args,
            context,
            result_callback,
            telephony_provider,
            call_id,
            bot_logger,
        ),
        "dtmf_output": lambda fn,
        tool_call_id,
        args,
        llm_svc,
        context,
        result_callback: dtmf_output_handler(
            fn,
            tool_call_id,
            args,
            context,
            result_callback,
            telephony_provider,
            call_id,
            bot_logger,
        ),
        "generic_function": lambda fn,
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
            bot_logger,
        ),
    }

    # Final tool list and registration
    all_tools = []
    for tool_dict, tool_name, handler_key in tool_candidates:
        all_tools.append(tool_dict)
        if handler_key:
            llm.register_function(tool_name, handler_map[handler_key])

    function_schemas = [tool_json_to_function_schema(tool) for tool in all_tools]
    tools_schema = ToolsSchema(standard_tools=function_schemas)

    # Pass the extracted vocab list to initialize_stt_service
    stt = initialize_stt_service(
        stt_provider=stt_provider,
        language=language,
        logger=bot_logger,
        record_locally=record_locally,
        vocab=vocab,  # Pass the vocab list here
    )

    tts = initialize_tts_service(
        tts_provider=tts_provider,
        language=language,
        voice=tts_voice,
        # Pass the function directly, the base TTSService will call it with dynamic lang_code
        text_formatter=format_tts_text,
        azure_api_key=api_config.AZURE_SPEECH_API_KEY,
        azure_region=api_config.AZURE_SPEECH_REGION,
        elevenlabs_api_key=api_config.ELEVENLABS_API_KEY,
        google_credentials_path="creds.json",  # Pass the relative path for Google creds
        deepgram_api_key=api_config.DEEPGRAM_API_KEY,
        cartesia_api_key=api_config.CARTESIA_API_KEY,
        tts_model=call_config.get(
            "tts_model", "sonic-2" if tts_provider == "cartesia" else "eleven_turbo_v2_5"
        ),
        voice_config=call_config.get("voice_config", {}),
    )

    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {"role": "assistant", "content": intro_message},
    ]

    # if llm_provider == "google":
    #     context = OpenAILLMContext(messages, tools)
    #     context = GoogleLLMContext.upgrade_to_google(context)
    # else:
    context = OpenAILLMContext(messages, tools_schema)

    # Add call_id and stream_id to context for end_call function
    context.call_id = call_id
    context.stream_id = stream_id
    context_aggregator = llm.create_context_aggregator(context)

    pipeline_steps = [
        transport.input(),  # Websocket input from client
    ]

    initialize_stt_mute_strategy(mute_during_intro, mute_while_bot_speaking, pipeline_steps)
    pipeline_steps.extend(
        [
            stt,
        ]
    )
    initialize_voicemail_detector(
        mute_during_intro,
        mute_while_bot_speaking,
        voicemail_detect,
        pipeline_steps,
        vad_params_bot_silent,
        lambda idle_proc: end_callback(
            idle_proc,
            telephony_provider,
            call_id,
            stream_id,
            websocket_client,
            callback_call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            function_call_monitor,
            bot_logger,
            None,
            record_locally,
        ),
    )
    initialize_hold_detector(
        call_hold_config,
        lambda idle_proc: end_callback(
            idle_proc,
            telephony_provider,
            call_id,
            stream_id,
            websocket_client,
            callback_call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            function_call_monitor,
            bot_logger,
            None,
            record_locally,
        ),
        pipeline_steps,
    )
    initialize_filler_config(call_config, transport, tts_voice, language, pipeline_steps)
    initialise_dtmf_input(call_config, pipeline_steps)
    user_idle = initialize_user_idle(
        idle_timeout_warning,
        idle_timeout_end,
        lambda idle_proc: end_callback(
            idle_proc,
            telephony_provider,
            call_id,
            stream_id,
            websocket_client,
            callback_call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            function_call_monitor,
            bot_logger,
            None,
            record_locally,
        ),
        lambda idle_proc: warning_callback(
            idle_proc, user_idle, context, function_call_monitor, bot_logger
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
        ]
    )

    # Add audio buffer processor to pipeline if needed
    if record_locally and audio_buffer:
        logger.debug("Adding audio_buffer")
        pipeline_steps.append(audio_buffer)

    pipeline_steps.extend(
        [
            transcript.assistant(),
            context_aggregator.assistant(),
        ]
    )

    pipeline = Pipeline(pipeline_steps)

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            audio_in_sample_rate=8000,
            audio_out_sample_rate=8000,
            start_metadata={
                "voicemail_detect": voicemail_detect,
                "call_id": callback_call_id or call_id,
            },
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        bot_logger.info("New client connection")
        # Start recording if enabled
        if record_locally and audio_buffer:
            await audio_buffer.start_recording()
        # Kick off the conversation.
        await tts.say(intro_message)
        # messages.append({"role": "system", "content": "Please introduce yourself to the user."})
        # await task.queue_frames([LLMMessagesFrame(messages)])

    # Register event handler for transcript updates
    @transcript.event_handler("on_transcript_update")
    async def on_transcript_update(processor, frame):
        await transcript_handler.on_transcript_update(processor, frame)

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        bot_logger.info("Client disconnected")

        # Stop audio recording if enabled
        if record_locally and audio_buffer:
            await audio_buffer.stop_recording()

        # close weaviate connection
        if call_config and call_config.get("user_rag", False):
            await weaviate_client.close()
        await cleanup_connection(
            callback_call_id,
            context_aggregator,
            transcript_handler,
            task,
            task_references,
            function_call_monitor,
            bot_logger,
            record_locally,
        )

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)
