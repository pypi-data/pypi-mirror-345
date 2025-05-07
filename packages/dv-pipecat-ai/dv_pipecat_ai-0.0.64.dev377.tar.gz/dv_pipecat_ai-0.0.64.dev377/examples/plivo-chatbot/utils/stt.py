from typing import List, Optional

from deepgram import LiveOptions  # noqa: D100
from env_config import api_config
from pipecat.services.azure.stt import AzureSTTService
from pipecat.services.deepgram.stt import DeepgramSTTService

# Import Gladia config models needed
from pipecat.services.gladia.config import GladiaInputParams, LanguageConfig
from pipecat.services.gladia.stt import GladiaSTTService, language_to_gladia_language
from pipecat.services.google.stt import GoogleSTTService
from pipecat.transcriptions.language import Language


# Add vocab parameter with type hint and default value
def initialize_stt_service(
    stt_provider, language, logger, record_locally=False, vocab: Optional[List[str]] = None
):
    if stt_provider == "deepgram":
        # Start with default keywords
        keywords = []
        if language.startswith("hi"):
            keywords.extend(["हाँ:1.5", "हाँ जी:1.5"])
        elif language.startswith("en"):
            keywords.extend(["ha:1.5", "haan:1.5"])

        # Add custom vocab if provided
        if vocab:
            logger.info(f"Adding custom vocab to Deepgram keywords: {vocab}")
            for word in vocab:
                # Ensure word is a string and not empty before adding
                if isinstance(word, str) and word.strip():
                    keywords.append(f"{word.strip()}:1.5")  # Add boost

        logger.info(f"Final Deepgram keywords: {keywords}")  # Log final list
        keywords = keywords if len(keywords) < 100 else keywords[:100]

        live_options = LiveOptions(
            model="nova-2-phonecall" if language.startswith("en") else "nova-2",
            language=language,
            # sample_rate=16000,
            encoding="linear16",
            channels=1,
            interim_results=True,
            smart_format=False,
            numerals=False,
            punctuate=True,
            profanity_filter=True,
            vad_events=False,
            keywords=keywords,  # Pass the combined list
        )
        stt = DeepgramSTTService(
            api_key=api_config.DEEPGRAM_API_KEY,
            live_options=live_options,
            audio_passthrough=record_locally,
            # metrics=SentryMetrics(),
        )
    elif stt_provider == "google":
        logger.debug("Google STT initilaising")
        languages = list({Language(language), Language.EN_IN})
        # list of languages you want to support; adjust if needed
        stt = GoogleSTTService(
            params=GoogleSTTService.InputParams(
                languages=languages, enable_automatic_punctuation=False, model="latest_short"
            ),
            credentials_path="creds.json",  # your service account JSON file,
            location="us",
            audio_passthrough=record_locally,
            # metrics=SentryMetrics(),
        )
        logger.debug("Google STT initiaised")
    elif stt_provider == "azure":
        logger.debug(
            f"Initializing Azure STT. Received language parameter: '{language}' (type: {type(language)})"
        )  # ADDED LOG
        # Explicitly check the condition and log the result
        # is_telugu = language == "te-IN"
        # additional_langs = [Language.EN_IN] if is_telugu else []
        # Note: Azure STT requires different handling (Phrase Lists) - see notes below.
        stt = AzureSTTService(
            api_key=api_config.AZURE_SPEECH_API_KEY,
            region=api_config.AZURE_SPEECH_REGION,
            language=Language(language),
            # additional_languages=additional_langs,
            audio_passthrough=record_locally,
            vocab=vocab,  # Pass vocab via kwargs
            # metrics=SentryMetrics(),
        )
    elif stt_provider == "gladia":
        params = GladiaInputParams(language_config=LanguageConfig(languages=[Language(language)]))

        stt = GladiaSTTService(
            api_key=api_config.GLADIA_API_KEY,
            params=params,  # Pass the configured params object
            audio_passthrough=record_locally,
            vocab=vocab,  # Pass vocab via kwargs
            # metrics=SentryMetrics(),
        )

    return stt
