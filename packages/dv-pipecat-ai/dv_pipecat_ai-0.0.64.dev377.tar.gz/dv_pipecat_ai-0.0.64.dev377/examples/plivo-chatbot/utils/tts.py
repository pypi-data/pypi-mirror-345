import hashlib  # Added for hashing cache keys
import io  # Added for handling bytes as files
import json
import re
import socket
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

import aiohttp
import numpy as np
import redis.asyncio as redis  # Added for Redis client type hinting
from fastapi import HTTPException
from loguru import logger
from num_to_words import num_to_word as num2words
from pydub import AudioSegment

from pipecat.audio.resamplers.soxr_resampler import SOXRAudioResampler
from pipecat.frames.frames import TTSAudioRawFrame
from pipecat.services.azure.tts import AzureTTSService
from pipecat.services.cartesia.tts import CartesiaHttpTTSService, CartesiaTTSService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.google.tts import GoogleTTSService
from pipecat.services.tts_service import TTSService
from pipecat.transcriptions.language import Language
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketTransport


def initialize_tts_service(
    tts_provider: str,
    language: str,
    voice: str,
    text_formatter: Optional[Callable[[str], str]] = None,
    **kwargs,
) -> TTSService:
    """Initializes and returns a TTSService instance based on the given configuration.

    Args:
        tts_provider: The TTS provider to use (e.g., "azure", "elevenlabs").
        language: The language code (e.g., "en-US").
        voice: The voice ID or name.
        text_formatter: Optional text processing function.
        **kwargs: Additional keyword arguments to pass to the TTSService constructor.

    Returns:
        A configured TTSService instance.
    """
    if tts_provider == "azure":
        # Determine primary language enum
        try:
            primary_language_enum = Language(language)
        except ValueError:
            logger.warning(f"Invalid primary language code '{language}', defaulting to en-IN.")
            primary_language_enum = Language.EN_IN
            language = "en-IN"  # Ensure language string matches the default enum

        additional_langs = None
        additional_voices = None

        # Conditionally set additional languages/voices based on the primary language string
        if language.startswith("te"):
            additional_langs = ["en-IN"]
            # Using a common default voice, can be made configurable if needed
            additional_voices = {"en-IN": voice}
            logger.info(
                "Primary language is Telugu (te-IN), adding en-IN as additional TTS language."
            )

        # Initialize AzureTTSService with primary and additional languages
        # Note: We pass the primary language enum and voice directly.
        # Create InputParams specifically for non-language SSML settings like rate.
        speed_config = kwargs.get("voice_config", {}).get("speed")
        azure_speed = str(speed_config) if speed_config is not None else "1.25"
        input_params = AzureTTSService.InputParams(rate=azure_speed)
        tts = AzureTTSService(
            api_key=kwargs.get("azure_api_key"),
            region=kwargs.get("azure_region"),
            params=input_params,  # Pass the SSML params
            language=primary_language_enum,
            voice=voice,
            additional_languages=additional_langs,
            additional_voices=additional_voices,
            text_formatter=text_formatter,
        )
    elif tts_provider == "elevenlabs":
        tts_model = kwargs.get("tts_model", "eleven_turbo_v2_5")
        speed_config = kwargs.get("voice_config", {}).get("speed")
        elevenlabs_speed = 1.0  # Default float value
        if speed_config is not None:
            try:
                elevenlabs_speed = float(speed_config)
            except ValueError:
                logger.warning(
                    f"Invalid speed value '{speed_config}' for ElevenLabs, using default {elevenlabs_speed}."
                )

        input_params = ElevenLabsTTSService.InputParams(
            language=Language(language), speed=elevenlabs_speed
        )
        tts = ElevenLabsTTSService(
            api_key=kwargs.get("elevenlabs_api_key"),
            voice_id=voice,
            params=input_params,
            model=tts_model,
            sample_rate=16000,
            text_formatter=text_formatter,
        )
    elif tts_provider == "google":
        speed_config = kwargs.get("voice_config", {}).get("speed")
        google_speed = str(speed_config) if speed_config is not None else "1.25"
        input_params = GoogleTTSService.InputParams(language=Language(language), rate=google_speed)
        tts = GoogleTTSService(
            credentials_path=kwargs.get("google_credentials_path"),
            voice_id=voice,
            params=input_params,
            text_formatter=text_formatter,
        )
    elif tts_provider == "deepgram":
        tts = DeepgramTTSService(
            api_key=kwargs.get("deepgram_api_key"),
            voice=voice,
            text_formatter=text_formatter,
        )
    elif tts_provider == "cartesia":
        speed_config = kwargs.get("voice_config", {}).get("speed")
        cartesia_speed = str(speed_config) if speed_config is not None else "1.0"
        input_params = CartesiaTTSService.InputParams(
            language=Language(language), speed=cartesia_speed
        )
        tts_model = kwargs.get("tts_model", "sonic")
        if language == "hi":
            tts = CartesiaHttpTTSService(
                api_key=kwargs.get("cartesia_api_key"),
                voice_id=voice,
                params=input_params,
                model=tts_model,
                text_formatter=text_formatter,
            )
        else:
            tts = CartesiaTTSService(
                api_key=kwargs.get("cartesia_api_key"),
                voice_id=voice,
                params=input_params,
                model=tts_model,
                text_formatter=text_formatter,
            )
    else:
        raise ValueError(f"Unsupported TTS provider: {tts_provider}")

    return tts


def is_hindi(text):
    hindi_chars = re.findall(r"[\u0900-\u097F]+", text)
    hindi_chars_count = sum(len(word) for word in hindi_chars)
    threshold = 0.5
    return hindi_chars_count / len(text) > threshold if text else False


# Language-specific mappings
CURRENCY_UNITS = {
    "en": {
        "₹": ("rupees", "paisa"),
        "$": ("dollars", "cents"),
        "€": ("euros", "cents"),
        "£": ("pounds", "pence"),
    },
    "hi": {"₹": ("रुपये", "पैसे"), "$": ("डॉलर", "सेंट"), "€": ("यूरो", "सेंट"), "£": ("पाउंड", "पेंस")},
}

MONTH_NAMES = {
    "en": [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ],
    "hi": [
        "जनवरी",
        "फरवरी",
        "मार्च",
        "अप्रैल",
        "मई",
        "जून",
        "जुलाई",
        "अगस्त",
        "सितंबर",
        "अक्टूबर",
        "नवंबर",
        "दिसंबर",
    ],
}

SYMBOL_TRANSLATIONS = {
    "en": {
        "@": "at",
        "#": "hash",
        "%": "percent",
        "&": "and",
        "+": "plus",
        "=": "equals",
        "_": "underscore",
    },
    "hi": {
        "@": "एट",
        "#": "हैश",
        "%": "प्रतिशत",
        "&": "और",
        "+": "जोड़",
        "=": "बराबर",
        "_": "अंडरस्कोर",
    },
}


def my_num2words(n, lang):
    if isinstance(n, float):
        integer_part = int(n)
        frac_str = str(n).split(".")[1]
        int_words = my_num2words(integer_part, lang)
        frac_words = " ".join(num2words(int(d), lang=lang) for d in frac_str)
        return f"{int_words} point {frac_words}"
    else:
        return num2words(n, lang=lang).replace(",", "")  # Remove commas for TTS


def format_tts_text(text: str, lang_code: str = "en-IN") -> str:
    # Extract base language code (first 2 letters)
    lang = lang_code[0:2]
    # Only override with Hindi detection if explicitly using Hindi/English locale
    if lang in ["hi", "en"]:
        lang = "hi" if is_hindi(text) else "en"
    symbols = SYMBOL_TRANSLATIONS.get(lang, SYMBOL_TRANSLATIONS["en"])
    month_names = MONTH_NAMES.get(lang, MONTH_NAMES["en"])

    # Preprocessing
    text = re.sub(r"[―–—]", "-", text)

    # Currency handling
    def replace_currency(match):
        symbol = match.group(1)
        amount_str = match.group(2).replace(",", "")
        scale = match.group(3)
        units = CURRENCY_UNITS.get(lang, CURRENCY_UNITS["en"])[symbol]
        if "." in amount_str:
            integer_part, fractional_part = amount_str.split(".", 1)
            fractional_part = fractional_part.ljust(2, "0")[:2]
            frac_num = int(fractional_part)
            frac_words = f"{my_num2words(frac_num, lang)} {units[1]}" if frac_num > 0 else ""
            integer_num = int(integer_part)
        else:
            integer_num = int(amount_str)
            frac_words = ""
        int_words = my_num2words(integer_num, lang) + (f" {scale.lower()}" if scale else "")
        result = f"{int_words} {units[0]}"
        if frac_words:
            result += f" {frac_words}"
        return result

    text = re.sub(
        r"(\$|₹|€|£)\s*(\d+(?:[\d,.]*)?)\s*(lakhs?|crores?|k|m)?\b", replace_currency, text
    )

    # Phone number processing , "hi": ["दोहरा", "तिहरा"]
    repetition_terms = {"en": ["double", "triple"]}.get(lang, ["double", "triple"])

    def partition_run(count):
        groups = []
        while count > 0:
            if count == 4:  # Split four repeats into two doubles
                groups.extend([2, 2])
                count = 0
            elif count >= 3:  # Use triple for three repeats
                groups.append(3)
                count -= 3
            elif count == 2:  # Use double for two repeats
                groups.append(2)
                count -= 2
            else:  # Single digit
                groups.append(1)
                count -= 1
        return groups

    # Helper function to process phone numbers
    def process_phone(number):
        result = []
        i = 0
        while i < len(number):
            current = number[i]
            run_length = 1
            j = i + 1
            if lang == "en":
                while j < len(number) and number[j] == current:
                    run_length += 1
                    j += 1
            if run_length > 1:
                groups = partition_run(run_length)
                for group in groups:
                    digit_word = num2words(int(current), lang=lang)
                    if group == 2:
                        result.append(f"{repetition_terms[0]} {digit_word}")
                    elif group == 3:
                        result.append(f"{repetition_terms[1]} {digit_word}")
                    else:
                        result.append(digit_word)
            else:
                result.append(num2words(int(current), lang=lang))
            i = j
        return " ".join(result)

    text = re.sub(
        r"(\+\d{1,3}[- ]?)?(\d{10})",  # Match +91 or standalone 10-digit numbers
        lambda m: process_phone(re.sub(r"\D", "", m.group(2)[-10:]))
        if m.group(1) and m.group(1).startswith("+91")
        else process_phone(re.sub(r"\D", "", m.group(0))),
        text,
    )
    text = re.sub(r"([@#%&=+_=])", lambda m: f" {symbols[m.group(1)]} ", text)
    # Date handling
    # current_year = datetime.now().year
    current_year = 2025

    def replace_date_extended(match):
        day = match.group(1)
        month_part = match.group(2)
        year_part = match.group(4)
        day_word = my_num2words(int(day), lang)
        if month_part.isdigit():
            month_index = int(month_part)
            month_word = month_names[month_index - 1] if 1 <= month_index <= 12 else month_part
        else:
            candidate = month_part.lower()
            month_word = next(
                (name for name in month_names if name.lower().startswith(candidate)), month_part
            )
        if year_part:
            full_year = (
                int(year_part)
                if len(year_part) == 4
                else (
                    2000 + int(year_part)
                    if int(year_part) <= current_year % 100
                    else 1900 + int(year_part)
                )
            )
            year_word = my_num2words(full_year, lang)
            return (
                f"{day_word} {month_word}, {year_word}"
                if full_year != current_year
                else f"{day_word} {month_word}"
            )
        return f"{day_word} {month_word}"

    text = re.sub(
        r"\b(\d{1,2})[-/](\d{1,2}|[A-Za-z]+)([-/](\d{2,4}))?\b", replace_date_extended, text
    )

    # Time handling
    text = re.sub(
        r"(\d{1,2}):(\d{2})(?:\s*([AaPp][Mm]))?",
        lambda m: f"{my_num2words(int(m.group(1)) % 12 or 12, lang)} {'' if int(m.group(2)) == 0 else my_num2words(int(m.group(2)), lang)} {m.group(3) or ('PM' if int(m.group(1)) >= 12 else 'AM')}",
        text,
    )

    # URL/Email handling
    text = re.sub(
        r"\b(https?://\S+|www\.\S+)\b",
        lambda m: " ".join(symbols.get(c, c) for c in m.group().lower()),
        text,
    )
    text = re.sub(
        r"\b(\w+@\w+\.\w+)\b",
        lambda m: " ".join(symbols.get(c, c) for c in m.group().lower()),
        text,
    )

    # Handle standalone decimal numbers first
    text = re.sub(r"\b(\d+\.\d+)\b", lambda m: my_num2words(float(m.group()), lang), text)

    text = re.sub(
        r"\b\d{1,3}(,\d{2,3})+(?!\d)\b", lambda m: num2words(m.group().replace(",", ""), lang), text
    )
    text = re.sub(r"\b(\d+)(st|nd|rd|th)\b", lambda m: my_num2words(int(m.group(1)), lang), text)
    text = re.sub(r"\b(\d{1,})\b", lambda m: my_num2words(int(m.group()), lang), text)

    # Clean up
    return " ".join(text.split())


# Helper function for TTS with caching, sending audio directly via transport
async def say_with_cache(
    tts_service,
    redis_client: redis.Redis,
    use_cache: bool,
    text: str,
    transport: FastAPIWebsocketTransport,
    logger,
):
    key = f"intro_tts_{hashlib.sha256(text.encode()).hexdigest()}"
    if use_cache and redis_client:
        try:
            cached_mp3 = await redis_client.get(key)
            if cached_mp3 and len(cached_mp3) > 4:
                logger.info(f"TTS cache hit for {key}")

                # Decode with FFmpeg
                seg = AudioSegment.from_file(io.BytesIO(cached_mp3), format="mp3")
                pcm_int16 = np.array(seg.get_array_of_samples(), dtype=np.int16)

                # Stereo → mono if needed
                if seg.channels > 1:
                    pcm_int16 = pcm_int16.reshape(-1, seg.channels).mean(axis=1).astype(np.int16)

                # Resample to 8 kHz if needed
                if seg.frame_rate != 8_000:
                    resampler = SOXRAudioResampler()
                    pcm_bytes = pcm_int16.tobytes()
                    resampled_bytes = await resampler.resample(pcm_bytes, seg.frame_rate, 8_000)
                    pcm_int16 = np.frombuffer(resampled_bytes, dtype=np.int16)

                # Stream in 20 ms blocks
                block_size = 160  # 160 samples @ 8 kHz = 20 ms
                for start in range(0, len(pcm_int16), block_size):
                    chunk = pcm_int16[start : start + block_size]
                    if not chunk.size:
                        break
                    frame = TTSAudioRawFrame(
                        audio=chunk.tobytes(),
                        sample_rate=8_000,
                        num_channels=1,
                    )
                    await transport.output().send_audio(frame)

                logger.info("Finished cached playback.")
                return True
            else:
                logger.info(f"TTS cache miss for {key}")
        except Exception as e:
            logger.error(f"Redis/decode error for {key}: {e}")

    # Fallback
    logger.info("Using live TTS service (via pipeline).")
    await tts_service.say(text)
    return False


async def resample_to_8k_mp3_and_cache(
    redis_client: redis.Redis,
    text: str,
    mp3_bytes: bytes,
    ttl_seconds: int = 86_400,  # one day
    out_bitrate: str = "24k",  # keep file tiny, still good enough for 8 kHz
) -> str:
    """
    • Decode original MP3 (any sample‑rate) to PCM.
    • soxr‑resample → 8 kHz mono.
    • Re‑encode to MP3 @ 8 kHz (bit‑rate ~24 kbps).
    • Push compressed result into Redis.
    """
    # -- 1. decode ----------------------------------------------------------
    original = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")

    # -- 2. soxr resample to 8 kHz mono PCM --------------------------------
    pcm = original.set_channels(1).get_array_of_samples()
    pcm_np = pcm.tobytes()  # raw little‑endian 16‑bit
    resampled = soxr.resample(
        pcm_np,
        original.frame_rate,
        8_000,
        channels=1,
        input_dtype="int16",
        output_dtype="int16",
    )

    # -- 3. wrap back into AudioSegment & encode MP3 ------------------------
    seg = AudioSegment(resampled.tobytes(), frame_rate=8_000, sample_width=2, channels=1)
    buf = io.BytesIO()
    seg.export(buf, format="mp3", bitrate=out_bitrate)
    mp3_8k_bytes = buf.getvalue()

    # -- 4. store in Redis --------------------------------------------------
    key = f"intro_tts_{hashlib.sha256(text.encode()).hexdigest()}"
    await redis_client.set(key, mp3_8k_bytes, ex=ttl_seconds)
    logger.info(
        "Cached {} (size={} kB, TTL={} s)".format(key, len(mp3_8k_bytes) // 1024, ttl_seconds)
    )
    return key


# This function is for testing the cache_tts_mp3 function
async def cache_tts_mp3(
    redis_client: redis.Redis,
    text: str,
    mp3_bytes: bytes,
    ttl_seconds: int = 10_000,
) -> str:
    """
    Cache an MP3 blob so `say_with_cache()` can play it later.
    Returns the Redis key used, so callers can log/inspect.
    """
    key = f"intro_tts_{hashlib.sha256(text.encode()).hexdigest()}"
    try:
        # binary‑safe: Redis stores the raw bytes as‑is
        await redis_client.set(name=key, value=mp3_bytes, ex=ttl_seconds)
        logger.info("Cached TTS audio under {} (TTL={} s)".format(key, ttl_seconds))
    except Exception as exc:
        logger.error("Failed to cache TTS audio: {}".format(exc))
    return key


# This function is for testing the cache_tts_mp3 function
# ffmpeg -i test_cache.mp3 \
#        -ar 8000 \
#        -ac 1 \
#        -codec:a libmp3lame \
#        -b:a 16k \
#        test_cache_8k.mp3
async def put_file_on_redis(redis_client, text: str, filename: str):
    mp3_bytes = Path(filename).read_bytes()
    return await cache_tts_mp3(redis_client, text, mp3_bytes)


# Corrected function
async def get_tts_file_from_redis(redis_client: redis.Redis, text: str, output_dir: str = "."):
    """Retrieves MP3 bytes from Redis and saves them to a file."""
    await say_with_cache(None, redis_client, True, text, None, logger)
    key = f"intro_tts_{hashlib.sha256(text.encode()).hexdigest()}"
    mp3_bytes = await redis_client.get(key)

    print(f"Retrieved bytes for key {key}: {len(mp3_bytes) if mp3_bytes else 'None'}")

    if mp3_bytes:
        print(mp3_bytes[:4])
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Construct filename using the hash key
        filename = output_path / f"{key}.mp3"
        try:
            with open(filename, "wb") as f:
                f.write(mp3_bytes)
            print(f"Successfully saved MP3 to: {filename}")
            return str(filename)  # Return the path to the saved file
        except Exception as e:
            print(f"Error saving MP3 file {filename}: {e}")
            return None
    else:
        print(f"No data found in Redis for key: {key}")
        return None
