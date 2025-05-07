from backchannel import BackchannelProcessor
from hold_detector import HoldDetector
from voicemail_detector import VoicemailDetector

from pipecat.processors.dtmf_aggregator import DTMFAggregator
from pipecat.processors.filters.stt_mute_filter import (
    STTMuteConfig,
    STTMuteFilter,
    STTMuteStrategy,
)
from pipecat.processors.two_stage_user_idle_processor import TwoStageUserIdleProcessor
from pipecat.processors.user_idle_processor import UserIdleProcessor


def initialize_stt_mute_strategy(mute_during_intro, mute_while_bot_speaking, pipeline_steps):
    if mute_during_intro or mute_while_bot_speaking:
        # Mute during first speech only
        mute_strategy = {STTMuteStrategy.FUNCTION_CALL}
        if mute_during_intro:
            mute_strategy.add(STTMuteStrategy.MUTE_UNTIL_FIRST_BOT_COMPLETE)
        if mute_while_bot_speaking:
            mute_strategy.add(STTMuteStrategy.ALWAYS)
        stt_mute_filter_config = STTMuteConfig(strategies=mute_strategy)
        stt_mute_filter = STTMuteFilter(config=stt_mute_filter_config)
        pipeline_steps.append(stt_mute_filter)


def initialize_voicemail_detector(
    mute_during_intro,
    mute_while_bot_speaking,
    voicemail_detect,
    pipeline_steps,
    vad_params_bot_silent,
    end_callback,
):
    if mute_during_intro or mute_while_bot_speaking:
        # Processor to handle voicemail and when the user puts the call on hold.
        if voicemail_detect:
            voicemail_detector = VoicemailDetector(
                end_callback=end_callback, vad_params_bot_silent=vad_params_bot_silent
            )
            pipeline_steps.append(voicemail_detector)


def initialize_filler_config(call_config, transport, tts_voice, language, pipeline_steps):
    if call_config.get("filler_config", {}).get("enable_filler_words", False):
        backchannel_processor = BackchannelProcessor(
            transport=transport.output(),
            backchannel_base_dir="fillers",
            voice=tts_voice,
            words=call_config.get("filler_config", {}).get("filler_words", []),
            language=language,
            filler_frequency=call_config.get("filler_config", {}).get("filler_frequency", 0.2),
        )
        pipeline_steps.append(backchannel_processor)


def initialize_hold_detector(call_hold_config, end_callback, pipeline_steps):
    if call_hold_config.get("detect", False):
        hold_detector = HoldDetector(
            end_callback=end_callback, end_count=call_hold_config.get("end_count", 3)
        )
        pipeline_steps.append(hold_detector)


def initialize_user_idle(
    idle_timeout_warning,
    idle_timeout_end,
    end_callback,
    warning_callback,
):
    if idle_timeout_warning == 0 or idle_timeout_warning == idle_timeout_end:
        user_idle = UserIdleProcessor(callback=end_callback, timeout=idle_timeout_end)
    else:
        user_idle = TwoStageUserIdleProcessor(
            warning_timeout=idle_timeout_warning,
            end_timeout=idle_timeout_end,
            warning_callback=warning_callback,
            end_callback=end_callback,
        )

    return user_idle


def initialise_dtmf_input(call_config, pipeline_steps):
    """
    Adds DTMFAggregator to the pipeline_steps if dtmf_input is specified in call_config.
    """
    if call_config.get("dtmf_input"):
        dtmf_input = call_config.get("dtmf_input")
        dtmf_timeout = dtmf_input.get("timeout", 3.0)
        dtmf_digits = dtmf_input.get("digits")
        end_on_str = dtmf_input.get("end", "")
        reset_on_str = dtmf_input.get("reset", "")
        dtmf_end_on = set(end_on_str.split(",")) if end_on_str else set()
        dtmf_reset_on = set(reset_on_str.split(",")) if reset_on_str else set()
        dtmf_aggregator = DTMFAggregator(
            timeout=dtmf_timeout,
            digits=dtmf_digits,
            end_on=dtmf_end_on,
            reset_on=dtmf_reset_on,
        )
        pipeline_steps.extend([dtmf_aggregator])
