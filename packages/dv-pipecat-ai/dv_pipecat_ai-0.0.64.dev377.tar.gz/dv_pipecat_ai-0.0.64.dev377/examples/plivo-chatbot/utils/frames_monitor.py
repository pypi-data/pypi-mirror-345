import asyncio

# First-Party Imports
from pipecat.frames.frames import (
    BotSpeakingFrame,
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    VADParamsUpdateFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

# Local Application Imports


class BotSpeakingFrameMonitor(FrameProcessor):
    def __init__(self, final_message_done_event, vad_params_idle, vad_params_speaking, **kwargs):
        super().__init__(**kwargs)
        self.final_message_done_event = final_message_done_event
        self.waiting_for_final_message = False
        self.last_frame_time = None
        self.vad_params_idle = vad_params_idle
        self.vad_params_speaking = vad_params_speaking

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        await self.push_frame(frame, direction)
        if self.vad_params_speaking:
            if isinstance(frame, BotStoppedSpeakingFrame):
                await self.push_frame(
                    VADParamsUpdateFrame(self.vad_params_idle), FrameDirection.UPSTREAM
                )

            elif isinstance(frame, BotStartedSpeakingFrame):
                await self.push_frame(
                    VADParamsUpdateFrame(self.vad_params_speaking), FrameDirection.UPSTREAM
                )
        if self.waiting_for_final_message and isinstance(frame, BotSpeakingFrame):
            self.last_frame_time = asyncio.get_event_loop().time()
