#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import io
import wave
from abc import abstractmethod
from typing import Any, AsyncGenerator, Dict, Mapping, Optional

from loguru import logger

from pipecat.frames.frames import (
    AudioRawFrame,
    Frame,
    StartFrame,
    STTMuteFrame,
    STTUpdateSettingsFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.ai_service import AIService
from pipecat.transcriptions.language import Language


class STTService(AIService):
    """STTService is a base class for speech-to-text services."""

    def __init__(
        self,
        audio_passthrough=False,
        # STT input sample rate
        sample_rate: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._audio_passthrough = audio_passthrough
        self._init_sample_rate = sample_rate
        self._sample_rate = 0
        self._settings: Dict[str, Any] = {}
        self._muted: bool = False
        # Custom fields from ai_services.py for voicemail and first speech handling
        self._first_speech_handled: bool = False
        self._voicemail_detect: bool = False

    @property
    def is_muted(self) -> bool:
        """Returns whether the STT service is currently muted."""
        return self._muted

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    async def set_model(self, model: str):
        self.set_model_name(model)

    async def set_language(self, language: Language):
        pass

    @abstractmethod
    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        """Returns transcript as a string"""
        pass

    async def start(self, frame: StartFrame):
        await super().start(frame)
        self._sample_rate = self._init_sample_rate or frame.audio_in_sample_rate
        if hasattr(frame, "metadata") and "voicemail_detect" in frame.metadata:
            self._voicemail_detect = frame.metadata["voicemail_detect"]

    async def _update_settings(self, settings: Mapping[str, Any]):
        self.logger.info(f"Updating STT settings: {self._settings}")
        for key, value in settings.items():
            if key == "language":  # Add specific handling for language
                self.logger.info(f"Updating STT language setting to: [{value}]")
                await self.set_language(value)
                self._settings["language"] = value
            elif key in self._settings:
                self.logger.info(f"Updating STT setting {key} to: [{value}]")
                self._settings[key] = value
            elif key == "model":
                self.set_model_name(value)
            else:
                self.logger.warning(f"Unknown setting for STT service: {key}")

    async def process_audio_frame(self, frame: AudioRawFrame, direction: FrameDirection):
        # Only process audio if not muted, unless voicemail_detect is enabled and first speech not handled
        if self._muted and ((not self._voicemail_detect) or self._first_speech_handled):
            return
        await self.process_generator(self.run_stt(frame.audio))
        if hasattr(self, "_audio_passthrough") and self._audio_passthrough:
            await self.push_frame(frame, direction)

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Processes a frame of audio data, either buffering or transcribing it."""
        await super().process_frame(frame, direction)

        if isinstance(frame, AudioRawFrame):
            # In this service we accumulate audio internally and at the end we
            # push a TextFrame. We also push audio downstream in case someone
            # else needs it.
            await self.process_audio_frame(frame, direction)
            if self._audio_passthrough:
                await self.push_frame(frame, direction)
        elif isinstance(frame, STTUpdateSettingsFrame):
            await self._update_settings(frame.settings)
        elif isinstance(frame, STTMuteFrame):
            self._muted = frame.mute
            self.logger.debug(f"STT service {'muted' if frame.mute else 'unmuted'}")
            await self.push_frame(frame, direction)
        elif hasattr(frame, "BotStoppedSpeakingFrame"):
            if not self._first_speech_handled:
                self._first_speech_handled = True
            await self.push_frame(frame, direction)
        else:
            await self.push_frame(frame, direction)


class SegmentedSTTService(STTService):
    """SegmentedSTTService is an STTService that uses VAD events to detect
    speech and will run speech-to-text on speech segments only, instead of a
    continous stream. Since it uses VAD it means that VAD needs to be enabled in
    the pipeline.

    This service always keeps a small audio buffer to take into account that VAD
    events are delayed from when the user speech really starts.

    """

    def __init__(self, *, sample_rate: Optional[int] = None, **kwargs):
        super().__init__(sample_rate=sample_rate, **kwargs)
        self._content = None
        self._wave = None
        self._audio_buffer = bytearray()
        self._audio_buffer_size_1s = 0
        self._user_speaking = False

    async def start(self, frame: StartFrame):
        await super().start(frame)
        self._audio_buffer_size_1s = self.sample_rate * 2

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStartedSpeakingFrame):
            await self._handle_user_started_speaking(frame)
        elif isinstance(frame, UserStoppedSpeakingFrame):
            await self._handle_user_stopped_speaking(frame)

    async def _handle_user_started_speaking(self, frame: UserStartedSpeakingFrame):
        if frame.emulated:
            return
        self._user_speaking = True

    async def _handle_user_stopped_speaking(self, frame: UserStoppedSpeakingFrame):
        if frame.emulated:
            return

        self._user_speaking = False

        content = io.BytesIO()
        wav = wave.open(content, "wb")
        wav.setsampwidth(2)
        wav.setnchannels(1)
        wav.setframerate(self.sample_rate)
        wav.writeframes(self._audio_buffer)
        wav.close()
        content.seek(0)

        await self.process_generator(self.run_stt(content.read()))

        # Start clean.
        self._audio_buffer.clear()

    async def process_audio_frame(self, frame: AudioRawFrame, direction: FrameDirection):
        # If the user is speaking the audio buffer will keep growing.
        self._audio_buffer += frame.audio

        # If the user is not speaking we keep just a little bit of audio.
        if not self._user_speaking and len(self._audio_buffer) > self._audio_buffer_size_1s:
            discarded = len(self._audio_buffer) - self._audio_buffer_size_1s
            self._audio_buffer = self._audio_buffer[discarded:]
