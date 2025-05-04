from loguru import logger

from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    EmulateUserStartedSpeakingFrame,
    EmulateUserStoppedSpeakingFrame,
    Frame,
    LLMMessagesAppendFrame,
    STTMuteFrame,
    TranscriptionFrame,
    TTSSpeakFrame,
    VADParamsUpdateFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class VoicemailDetector(FrameProcessor):
    def __init__(self, end_callback, vad_params_bot_silent, **kwargs):
        super().__init__(**kwargs)
        self.end_callback = end_callback
        self.is_muted = False
        self._first_speech_handled = False
        self.voicemail_detected = False
        self.voicemail_phrases = ["leave a message", "after the tone", "voicemail", "voice mail"]
        self.vad_params_bot_silent = vad_params_bot_silent
        # self.final_message = final_message
        # self.delivering_final_message = False

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        # Update mute status
        if isinstance(frame, STTMuteFrame):
            self.logger.debug(f"Setting mute to {frame.mute}")
            self.is_muted = frame.mute
        # elif isinstance(frame, BotStartedSpeakingFrame):
        #     if self.voicemail_detected:
        #         self.delivering_final_message = True

        # Track bot speaking status and trigger voicemail callback. The bot is unmuted after userstopped speaking frame is handled at stt_mute_filter, so we listen to this earlier than that here.
        # elif isinstance(frame, BotStoppedSpeakingFrame):
        #     self._first_speech_handled = True
        #     logger.debug("First speech handled set to true")
        #     if self.delivering_final_message:
        #         await self.end_callback(None)

        # Process transcriptions for voicemail and hold detection
        elif isinstance(frame, TranscriptionFrame):
            text = frame.text.lower()
            if self.is_muted:
                self.logger.debug(f"Transcript Frame:{text}")
                # Voicemail detection
                if not self._first_speech_handled and any(
                    phrase in text for phrase in self.voicemail_phrases
                ):
                    self.logger.debug("Voicemail detected")
                    await self.push_frame(
                        VADParamsUpdateFrame(self.vad_params_bot_silent), FrameDirection.UPSTREAM
                    )
                    await self.push_frame(STTMuteFrame(mute=False), FrameDirection.UPSTREAM)
                    self.voicemail_detected = True
                    await self.push_frame(
                        LLMMessagesAppendFrame(
                            messages=[
                                {
                                    "role": "system",
                                    "content": "The user could not hear any of the previous messages. So, first give a summary as to who are you and why did you call and then, call the end_call tool with a final message: 'thank you'.",
                                }
                            ]
                        ),
                        FrameDirection.DOWNSTREAM,
                    )
            else:
                await self.push_frame(frame, direction)

        else:
            await self.push_frame(frame, direction)
