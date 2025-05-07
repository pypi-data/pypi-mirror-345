import asyncio  # noqa: D100
import io
import json
import wave
from pathlib import Path
from typing import List

import aioboto3
import aiofiles
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from env_config import api_config
from loguru import logger
from pydub import AudioSegment

from pipecat.frames.frames import TranscriptionMessage, TranscriptionUpdateFrame
from pipecat.processors.transcript_processor import TranscriptProcessor, UserTranscriptProcessor

load_dotenv(override=True)

# Initialize aioboto3 session
session = aioboto3.Session(
    aws_access_key_id=api_config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=api_config.AWS_SECRET_ACCESS_KEY,
    region_name=api_config.AWS_REGION,
)

BUCKET_NAME = api_config.S3_BUCKET_NAME
TRANSCRIPT_FOLDER = "call-transcripts"
RECORDING_FOLDER = "call-recordings"
LOCAL_STORAGE_DIR = Path("/tmp/call-recordings")

# Ensure local storage directory exists
LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class TranscriptHandler:
    """Handles real-time transcript processing and output.

    Maintains a list of conversation messages and outputs them to a log
    as they are received. Each message includes its timestamp and role.

    Attributes:
        messages: List of all processed transcript messages
    """

    def __init__(self, logger):
        """Initialize handler with log output."""
        self.messages: List[TranscriptionMessage] = []
        self.logger=logger

    async def on_transcript_update(
        self, processor: TranscriptProcessor, frame: TranscriptionUpdateFrame
    ):
        """Handle new transcript messages.

        Args:
            processor: The TranscriptProcessor that emitted the update
            frame: TranscriptionUpdateFrame containing new messages
        """
        self.logger.debug(f"Received transcript update with {len(frame.messages)} new messages")

        for msg in frame.messages:
            self.messages.append(msg)


async def save_audio_to_file(
    audio_data: bytes, sample_rate: int, num_channels: int, call_id: str
) -> str:
    """Save raw audio to a local file, appending if the file already exists."""
    try:
        # Define the file paths
        raw_path = LOCAL_STORAGE_DIR / f"{call_id}.raw"
        metadata_path = LOCAL_STORAGE_DIR / f"{call_id}.meta"

        logger.debug(f"Saving {len(audio_data)} bytes of audio to {raw_path}")

        # Open in append mode to handle existing files
        async with aiofiles.open(raw_path, "ab") as f:
            await f.write(audio_data)

        # Store metadata in a separate file if it doesn't exist yet
        if not metadata_path.exists():
            metadata = {"sample_rate": sample_rate, "num_channels": num_channels}
            async with aiofiles.open(metadata_path, "w") as f:
                await f.write(json.dumps(metadata))

        return str(raw_path)
    except Exception as e:
        logger.error(f"Error saving audio to file: {str(e)}")
        return None


async def save_to_s3(
    data: bytes, content_type: str, file_extension: str, folder: str, call_id: str
) -> str | None:
    """Upload data to S3."""
    try:
        logger.info(f"Uploading {len(data)} bytes to S3 for call {call_id}")
        async with session.client("s3") as s3:
            await s3.put_object(
                Bucket=BUCKET_NAME,
                Key=f"{folder}/{call_id}.{file_extension}",
                Body=data,
                ContentType=content_type,
            )
        logger.info(f"Successfully uploaded to S3 for call {call_id}")
        recording_url = f"https://{BUCKET_NAME}.s3.{api_config.AWS_REGION}.amazonaws.com/{folder}/{call_id}.{file_extension}"
        return recording_url
    except Exception as e:
        logger.error(f"Error saving to S3: {str(e)}")
        return None


async def upload_recording_to_s3(call_id: str) -> str | None:
    """Convert raw audio file to MP3 and upload to S3."""
    try:
        raw_path = LOCAL_STORAGE_DIR / f"{call_id}.raw"
        metadata_path = LOCAL_STORAGE_DIR / f"{call_id}.meta"

        # Check if the files exist, wait if not
        for attempt in range(6):  # Try up to 6 times with increasing delay
            if raw_path.exists() and metadata_path.exists():
                break

            wait_time = min(5, attempt + 1)  # Progressive backoff: 1s, 2s, 3s, 4s, 5s
            logger.info(
                f"Waiting {wait_time}s for audio files for call {call_id} (attempt {attempt + 1}/6)..."
            )
            await asyncio.sleep(wait_time)
        else:
            logger.error(f"Audio files for call {call_id} not found after waiting")
            return None

        # Read metadata
        async with aiofiles.open(metadata_path, "r") as f:
            metadata = json.loads(await f.read())

        sample_rate = metadata["sample_rate"]
        num_channels = metadata["num_channels"]

        # Read raw audio data
        async with aiofiles.open(raw_path, "rb") as f:
            audio_data = await f.read()

        if not audio_data:
            logger.error(f"No audio data found for call {call_id}")
            return None

        logger.info(f"Converting and uploading {len(audio_data)} bytes of audio for call {call_id}")

        # Convert raw PCM to MP3
        with io.BytesIO() as wav_buffer:
            with wave.open(wav_buffer, "wb") as wf:
                wf.setsampwidth(2)  # 16-bit
                wf.setnchannels(num_channels)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data)

            wav_buffer.seek(0)
            audio = AudioSegment.from_wav(wav_buffer)

            # Export as MP3
            mp3_buffer = io.BytesIO()
            audio.export(mp3_buffer, format="mp3", bitrate="64k")
            mp3_buffer.seek(0)

            # Upload to S3
            recording_url = await save_to_s3(
                mp3_buffer.getvalue(), "audio/mpeg", "mp3", RECORDING_FOLDER, call_id
            )

            if recording_url:
                logger.info(f"Successfully uploaded recording for call {call_id}")
                # Clean up local files
                try:
                    raw_path.unlink()
                    metadata_path.unlink()
                    logger.debug(f"Cleaned up local files for call {call_id}")
                except Exception as e:
                    logger.warning(f"Failed to clean up local files for call {call_id}: {str(e)}")
                return recording_url
            else:
                logger.error(f"Failed to upload recording for call {call_id}")
                return None

    except Exception as e:
        logger.error(f"Error uploading audio recording: {str(e)}", exc_info=True)
        return None


async def store_transcript(call_id: str, transcript: list, should_upload_recording=False):
    """Store transcript and upload recording to S3."""
    # Filter out system messages
    filtered_transcript = (
        transcript[1:] if transcript and transcript[0].get("role") == "system" else transcript
    )

    try:
        # Convert transcript to JSON string
        transcript_json = json.dumps(filtered_transcript, ensure_ascii=False)
        transcript_stored = False

        # Upload transcript to S3
        try:
            async with session.client("s3") as s3:
                await s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=f"{TRANSCRIPT_FOLDER}/{call_id}.json",
                    Body=transcript_json,
                    ContentType="application/json",
                )
            transcript_stored = True
            logger.info(f"Transcript successfully uploaded to S3 for call {call_id}")
        except Exception as e:
            logger.error(f"Error storing transcript in S3: {str(e)}")
            # Fallback to local storage
            try:
                temp_file_path = Path(f"/tmp/{call_id}.json")
                async with aiofiles.open(temp_file_path, mode="w", encoding="utf-8") as f:
                    await f.write(transcript_json)
                logger.info(f"Transcript stored locally at: {temp_file_path}")
            except Exception as local_error:
                logger.error(f"Failed to store transcript locally: {str(local_error)}")

        # Upload the recording if requested
        if should_upload_recording:
            try:
                recording_url = await upload_recording_to_s3(call_id)
                if recording_url:
                    logger.info(f"Recording URL: {recording_url}")
            except Exception as e:
                logger.error(f"Error uploading recording: {str(e)}")

        return transcript_stored
    except Exception as e:
        logger.error(f"Error in store_transcript: {str(e)}", exc_info=True)
        return False


async def get_transcript_text(call_id: str):
    """Retrieve transcript from S3."""
    try:
        async with session.client("s3") as s3:
            # Get object from S3
            response = await s3.get_object(
                Bucket=BUCKET_NAME, Key=f"{TRANSCRIPT_FOLDER}/{call_id}.json"
            )
            # Read and parse JSON content
            async with response["Body"] as stream:
                data = await stream.read()
                transcript = json.loads(data.decode("utf-8"))
                return transcript
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return None
        logger.error(f"Error retrieving transcript from S3: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error retrieving transcript: {str(e)}")
        return None


def get_transcript_url(call_id: str) -> str:
    """Returns the S3 URL for the transcript
    """
    region = api_config.AWS_REGION
    return f"https://{BUCKET_NAME}.s3.{region}.amazonaws.com/{TRANSCRIPT_FOLDER}/{call_id}.json"


def get_recording_url(call_id: str) -> str:
    """Returns the S3 URL for the recording."""
    region = api_config.AWS_REGION
    return f"https://{BUCKET_NAME}.s3.{region}.amazonaws.com/{RECORDING_FOLDER}/{call_id}.mp3"
