from loguru import logger

from pipecat.frames.frames import Frame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class HoldDetector(FrameProcessor):
    def __init__(self, end_callback, end_count, **kwargs):
        super().__init__(**kwargs)
        self.end_callback = end_callback
        self.end_count = end_count
        self.hold_count = 0
        self.hold_phrases = ["call on hold", "hold the line"]  # Add more phrases as needed

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        await self.push_frame(frame, direction)
        if isinstance(frame, TranscriptionFrame):
            text = frame.text.lower()
            if any(phrase in text for phrase in self.hold_phrases):
                self.hold_count += 1
                self.logger.debug(f"Hold phrase detected. Count: {self.hold_count}")
                if self.hold_count >= self.end_count:
                    self.logger.info(f"Hold count exceeded. Ending call.")
                    await self.end_callback(None)
