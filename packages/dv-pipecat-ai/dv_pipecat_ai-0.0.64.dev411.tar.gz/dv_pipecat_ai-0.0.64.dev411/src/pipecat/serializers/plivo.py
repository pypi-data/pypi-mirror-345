import base64
import json
from typing import Optional

from pydantic import BaseModel

from pipecat.audio.utils import create_default_resampler, pcm_to_ulaw, ulaw_to_pcm
from pipecat.frames.frames import (
    AudioRawFrame,
    Frame,
    InputAudioRawFrame,
    InputDTMFFrame,
    KeypadEntry,
    StartFrame,
    StartInterruptionFrame,
    TransportMessageFrame,
    TransportMessageUrgentFrame,
)
from pipecat.serializers.base_serializer import FrameSerializer, FrameSerializerType


class PlivoFrameSerializer(FrameSerializer):
    class InputParams(BaseModel):
        plivo_sample_rate: int = 8000
        sample_rate: Optional[int] = None  # Pipeline input rate

    def __init__(self, stream_id: str, params: InputParams = InputParams()):
        self._stream_id = stream_id
        self._params = params

        self.plivo_sample_rate = self._params.plivo_sample_rate
        self._sample_rate = 0  # Pipeline input rate

        self._resampler = create_default_resampler()

    @property
    def type(self) -> FrameSerializerType:
        return FrameSerializerType.TEXT

    async def setup(self, frame: StartFrame):
        self._sample_rate = self._params.sample_rate or frame.audio_in_sample_rate

    async def serialize(self, frame: Frame) -> str | bytes | None:
        if isinstance(frame, StartInterruptionFrame):
            answer = {"event": "clearAudio", "streamId": self._stream_id}
            return json.dumps(answer)
        elif isinstance(frame, AudioRawFrame):
            data = frame.audio

            # Output: Convert PCM at frame's rate to 8kHz μ-law for Twilio
            serialized_data = await pcm_to_ulaw(
                data, frame.sample_rate, self.plivo_sample_rate, self._resampler
            )
            payload = base64.b64encode(serialized_data).decode("utf-8")
            answer = {
                "event": "playAudio",
                "streamId": self._stream_id,
                "media": {
                    "payload": payload,
                    "contentType": "audio/x-mulaw",
                    "sampleRate": self._params.plivo_sample_rate,
                },
            }

            return json.dumps(answer)
        elif isinstance(frame, (TransportMessageFrame, TransportMessageUrgentFrame)):
            return json.dumps(frame.message)

    async def deserialize(self, data: str | bytes) -> Frame | None:
        # print("Deserialising data", data)
        message = json.loads(data)

        if message["event"] == "media":
            payload_base64 = message["media"]["payload"]
            payload = base64.b64decode(payload_base64)
            # Input: Convert Plivo's 8kHz μ-law to PCM at pipeline input rate
            deserialized_data = await ulaw_to_pcm(
                payload, self.plivo_sample_rate, self._sample_rate, self._resampler
            )
            audio_frame = InputAudioRawFrame(
                audio=deserialized_data, num_channels=1, sample_rate=self._sample_rate
            )
            return audio_frame
        elif message["event"] == "dtmf":
            try:
                digit = message.get("dtmf", {}).get("digit")
                if digit is None:
                    print(f"Error processing DTMF: 'digit' key not present in message: {message}")
                    return None
                return InputDTMFFrame(KeypadEntry(digit))
            except (ValueError, KeyError) as e:
                # Handle case where string doesn't match any enum value or key is missing.
                print(f"Error processing DTMF: {e}")
                return None
        else:
            print(f"message: {message}")
            return None
