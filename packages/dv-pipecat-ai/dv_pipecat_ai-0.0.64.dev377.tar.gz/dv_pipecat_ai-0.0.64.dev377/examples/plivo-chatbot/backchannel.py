import asyncio
import os
import random

from loguru import logger

from pipecat.frames.frames import TranscriptionFrame, TTSAudioRawFrame
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.transports.base_output import BaseOutputTransport


class BackchannelProcessor(FrameProcessor):
    def __init__(
        self,
        transport: BaseOutputTransport,
        backchannel_base_dir: str,
        voice: str,
        words: list,
        language: str,
        filler_frequency: float,
        **kwargs,
    ):
        """Initialize the BackchannelTrigger processor.

        Args:
            transport (BaseOutputTransport): The output transport to send audio frames.
            backchannel_base_dir (str): Base directory containing backchannel audio files (e.g., 'backchannels').
            voice (str): The current voice (e.g., 'voice1', 'voice2').
            words (list): A list of filler words to use.
            language (str): The language of the filler words.
            filler_frequency (float): The probability (0 to 1) of playing a filler word.
        """
        super().__init__(**kwargs)
        self._transport = transport
        self._backchannel_base_dir = backchannel_base_dir
        self._voice = voice
        self._words = words
        self._language = language
        self._filler_frequency = filler_frequency
        self._sample_rate = 8000
        self._num_channels = 1  # Access via transport params

    async def process_frame(self, frame, direction):
        """Process incoming frames. If it's a TranscriptionFrame, trigger backchannel audio."""
        await super().process_frame(frame, direction)
        await self.push_frame(frame, direction)
        if isinstance(frame, TranscriptionFrame):
            await asyncio.sleep(0.3)  # Add a 0.3 second delay.  Adjust as needed.
            await self._play_backchannel()

    async def _play_backchannel(self):
        """
        Play a random backchannel (filler) audio using SoundfileMixer for mp3 support.
        """
        if not self._words:
            self.logger.info("No filler words provided.")
            return
        if random.random() > self._filler_frequency:
            return
        word = random.choice(self._words)
        filename = f"{word.replace(' ', '_')}.mp3"
        path = os.path.join(self._backchannel_base_dir, self._voice, filename)
        try:
            # Use soundfile to read mp3 data and convert to PCM
            import numpy as np
            import soundfile as sf

            audio_data, sample_rate = sf.read(path, dtype="int16")
            if sample_rate != self._sample_rate:
                # Resample if needed
                from pipecat.audio.resamplers.soxr_resampler import SOXRAudioResampler

                resampler = SOXRAudioResampler()
                audio_bytes = audio_data.astype(np.int16).tobytes()
                audio_bytes = await resampler.resample(audio_bytes, sample_rate, self._sample_rate)
                audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_bytes = audio_data.astype(np.int16).tobytes()
        except Exception as e:
            self.logger.error(f"Error reading backchannel audio file {path} with soundfile: {e}")
            return

        # Create a TTSAudioRawFrame with the audio data
        frame = TTSAudioRawFrame(
            audio=audio_bytes, sample_rate=self._sample_rate, num_channels=self._num_channels
        )

        # Send the audio frame directly to the output transport        await self._transport.send_audio(frame)
