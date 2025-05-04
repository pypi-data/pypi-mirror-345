# Standard Library Imports
import asyncio

# First-Party Imports
from pipecat.frames.frames import STTUpdateSettingsFrame, TTSUpdateSettingsFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.transcriptions.language import Language

# Define language mapping
LANGUAGE_MAP = {
    "english": Language.EN_IN,
    "hindi": Language.HI_IN,
    "telugu": Language.TE_IN,
    "tamil": Language.TA_IN,
    "kannada": Language.KN_IN,
    # Add more mappings as needed
}

# Define switch_language tool
switch_language_tool = {
    "name": "switch_language",
    "description": "Switch to this conversation language when the user asks explicitly asks you to do so.",
    "parameters": {
        "type": "object",
        "properties": {
            "language": {
                "type": "string",
                "description": "The target language name (e.g., 'telugu', 'english', 'hindi').",
            },
        },
        "required": ["language"],
    },
}


async def switch_language_handler(
    function_name: str,
    tool_call_id: str,
    args: dict,
    llm: FrameProcessor,
    context,
    result_callback: callable,
    bot_logger,
):
    language_name = args.get("language", "").lower()
    bot_logger.info(f"Attempting to switch STT language to: {language_name}")

    language_enum = LANGUAGE_MAP.get(language_name)

    if not language_enum:
        error_message = f"Sorry, I don't support the language '{language_name}' for STT."
        bot_logger.warning(error_message)
        await result_callback({"error": error_message})
        return

    try:
        # Update STT (Upstream)
        stt_update_frame = STTUpdateSettingsFrame(settings={"language": language_enum})
        await llm.push_frame(stt_update_frame, FrameDirection.UPSTREAM)
        bot_logger.info(f"Pushed STTUpdateSettingsFrame for {language_name} upstream")

        # Update TTS (Downstream)
        tts_update_frame = TTSUpdateSettingsFrame(settings={"language": language_enum})
        await llm.push_frame(tts_update_frame, FrameDirection.DOWNSTREAM)
        bot_logger.info(f"Pushed TTSUpdateSettingsFrame for {language_name} downstream")

        success_message = f"Switched language to {language_name}."
        bot_logger.info(success_message)
        await result_callback({"status": success_message})

    except Exception as e:
        error_message = f"An error occurred while switching language: {e}"
        bot_logger.exception(error_message)
        await result_callback({"error": error_message})
