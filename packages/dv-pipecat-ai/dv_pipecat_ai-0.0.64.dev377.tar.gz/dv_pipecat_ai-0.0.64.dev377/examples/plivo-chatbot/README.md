# Twilio Chatbot

This project is a FastAPI-based chatbot that integrates with Twilio to handle WebSocket connections and provide real-time communication. The project includes endpoints for starting a call and handling WebSocket connections.

#To deploy on remote Dv machine
On the root folder. run the following commands:
1. sudo docker build  -t plivo-chatbot -f examples/plivo-chatbot/Dockerfile .
(or) sudo docker build --no-cache -t plivo-chatbot -f examples/plivo-chatbot/Dockerfile .
2. sudo docker ps -a
3. sudo docker stop <Id of the running contianer>
4. sudo docker run -p 8765:8765 -d plivo-chatbot

## Table of Contents

- [Twilio Chatbot](#twilio-chatbot)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Configure Twilio URLs](#configure-twilio-urls)
  - [Running the Application](#running-the-application)
    - [Using Python](#using-python)
    - [Using Docker](#using-docker)
  - [Usage](#usage)

## Features

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.6+.
- **WebSocket Support**: Real-time communication using WebSockets.
- **CORS Middleware**: Allowing cross-origin requests for testing.
- **Dockerized**: Easily deployable using Docker.

## Requirements

- Python 3.10
- Docker (for containerized deployment)
- ngrok (for tunneling)
- Twilio Account

## Installation

1. **Set up a virtual environment** (optional but recommended):
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Create .env**:
    create .env based on env.example

4. **Install ngrok**:
    Follow the instructions on the [ngrok website](https://ngrok.com/download) to download and install ngrok.

## Configure Twilio URLs

1. **Start ngrok**:
    In a new terminal, start ngrok to tunnel the local server:
    ```sh
    ngrok http 8765
    ```

2. **Update the Twilio Webhook**:
    Copy the ngrok URL and update your Twilio phone number webhook URL to `http://<ngrok_url>/start_call`.

3. **Update streams.xml**:
    Copy the ngrok URL and update templates/streams.xml with `wss://<ngrok_url>/ws`.

## Running the Application

### Using Python

1. **Run the FastAPI application**:
    ```sh
    python server.py
    ```

### Using Docker

1. **Build the Docker image**:
    ```sh
    docker build -t twilio-chatbot .
    ```

2. **Run the Docker container**:
    ```sh
    docker run -it --rm -p 8765:8765 twilio-chatbot
    ```
## Usage

To start a call, simply make a call to your Twilio phone number. The webhook URL will direct the call to your FastAPI application, which will handle it accordingly.



1. ngrok http 8765
2. Put the ngrok url in the .env file https://8bde-4-186-62-155.ngrok-free.app
3. pip install -r dev-requirements.txt
4. pip install -r examples/plivo-chatbot/requirements.txt
5. To use local: pip install --editable ".[daily,cartesia,openai,silero,deepgram,azure,elevenlabs,google]" -> This should be run in the root dir
6. cd examples/plivo-chatbot
7. python server.py

#To convert mp3 to pcm for fillers:
ffmpeg -i examples/plivo-chatbot/fillers/en-IN-RehaanNeural/en_got_it.mp3 -acodec pcm_s16le -ar 8000 -ac 1 -f s16le examples/plivo-chatbot/fillers/en-IN-RehaanNeural/en_got_it.pcm
