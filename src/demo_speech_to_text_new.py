#!/usr/bin/env python3
# demo_speech_to_text.py
# Transcribe an audio file using Azure AI Speech SDK.
import os
from env_loader import load_dotenv

def main():
    load_dotenv()
    try:
        import azure.cognitiveservices.speech as speechsdk
    except Exception:
        raise RuntimeError("Install SDK: pip install azure-cognitiveservices-speech")
    speech_key = os.environ.get("AZURE_SPEECH_KEY", "")
    speech_region = os.environ.get("AZURE_SPEECH_REGION", "")
    audio_path = os.environ.get("SPEECH_AUDIO_PATH", "../data/audio/Recording.wav")
    assert speech_key and speech_region, "Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in .env"

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    audio_config = speechsdk.AudioConfig(filename=audio_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    print("Transcribing:", audio_path)
    result = recognizer.recognize_once_async().get()
    print("Result:", getattr(result, "text", result))

if __name__ == "__main__":
    main()
