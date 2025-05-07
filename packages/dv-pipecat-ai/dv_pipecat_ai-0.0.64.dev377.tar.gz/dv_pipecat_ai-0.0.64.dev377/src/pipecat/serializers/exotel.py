#
# Copyright (c) 2024, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import base64
import json

from pydantic import BaseModel

from pipecat.audio.utils import create_default_resampler, pcm_to_ulaw, ulaw_to_pcm
from pipecat.frames.frames import (
    AudioRawFrame,
    Frame,
    InputAudioRawFrame,
    InputDTMFFrame,
    KeypadEntry,
    StartInterruptionFrame,
)
from pipecat.serializers.base_serializer import FrameSerializer, FrameSerializerType


class ExotelFrameSerializer(FrameSerializer):
    class InputParams(BaseModel):
        exotel_sample_rate: int = 8000
        sample_rate: int = 16000

    def __init__(self, stream_sid: str, params: InputParams = InputParams()):
        self._stream_sid = stream_sid
        self._params = params

        self._exotel_sample_rate = self._params.exotel_sample_rate
        self._sample_rate = self._params.sample_rate

        self._resampler = create_default_resampler()

    @property
    def type(self) -> FrameSerializerType:
        return FrameSerializerType.TEXT

    async def serialize(self, frame: Frame) -> str | bytes | None:
        if isinstance(frame, AudioRawFrame):
            data = frame.audio

            serialized_data = await self._resampler.resample(
                data, frame.sample_rate, self._exotel_sample_rate
            )
            payload = base64.b64encode(serialized_data).decode("utf-8")
            answer = {
                "event": "media",
                "stream_sid": self._stream_sid,
                "media": {"payload": payload},
            }

            return json.dumps(answer)

        if isinstance(frame, StartInterruptionFrame):
            answer = {"event": "clear", "stream_sid": self._stream_sid}
            return json.dumps(answer)

    async def deserialize(self, data: str | bytes) -> Frame | None:
        message = json.loads(data)

        if message["event"] == "media":
            payload_base64 = message["media"]["payload"]
            deserialized_data = base64.b64decode(payload_base64)
            # Exotel sends 8kHz, 16-bit mono PCM
            # Resample to 16kHz for downstream
            deserialized_data = await self._resampler.resample(
                deserialized_data, self._exotel_sample_rate, self._sample_rate
            )

            audio_frame = InputAudioRawFrame(
                audio=deserialized_data, num_channels=1, sample_rate=self._sample_rate
            )
            return audio_frame
        elif message["event"] == "dtmf":
            try:
                digit = message.get("dtmf", {}).get("digit")
                return InputDTMFFrame(KeypadEntry(digit))
            except Exception as e:
                # Handle case where string doesn't match any enum value
                return None
        return None
