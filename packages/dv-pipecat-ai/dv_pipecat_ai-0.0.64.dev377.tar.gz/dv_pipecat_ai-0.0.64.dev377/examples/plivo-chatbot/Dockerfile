FROM python:3.12-bullseye

WORKDIR /app

# copy in your built wheel(s)
COPY dist/ /app/dist/

# install the newest wheel with extras
RUN set -eux; \
    # pick the newest .whl in /app/dist
    WHEEL=$(ls -1t /app/dist/*.whl | head -1); \
    echo "Installing wheel: $WHEEL"; \
    pip install --no-cache-dir \
    "${WHEEL}[daily,cartesia,openai,silero,deepgram,azure,elevenlabs,noisereduce,gladia,google,groq,sentry]"

# install ffmpeg for audio
RUN apt-get update && apt-get install -y ffmpeg

# install example requirements
COPY examples/plivo-chatbot/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy your app
COPY examples/plivo-chatbot/ /app/

EXPOSE 8765
CMD ["python", "server.py"]