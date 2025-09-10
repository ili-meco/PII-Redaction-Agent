#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo_script.py
-------------
Azure AI Foundry Day 1 Demos – code snippets you can run piece‑by‑piece in VS Code.
Each section is self-contained. Replace the placeholders with your values.
Recommended: set secrets as environment variables instead of hardcoding.

Prereqs (pick what you need):
- Python 3.10+
- pip install requests azure-cognitiveservices-speech
- For Document Intelligence: use REST (requests) or the latest Azure AI Document Intelligence SDK.
- Audio test file for Speech‑to‑Text: put sample.wav in the same folder.

Environment variables (recommended):
- AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION
- AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
- AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_REGION
- AZURE_DOCINTEL_KEY, AZURE_DOCINTEL_ENDPOINT
"""

import os
import json
import time
import base64
from typing import Any, Dict, List
from pathlib import Path

import requests

# Load environment variables from .env file if it exists
def load_env_file(env_path=".env"):
    """Load environment variables from a .env file"""
    env_file = Path(env_path)
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key, value = key.strip(), value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value

# Try to load .env file at module import
load_env_file()

# Optional import for Speech. Install only if you plan to run the Speech demo.
try:
    import azure.cognitiveservices.speech as speechsdk  # pip install azure-cognitiveservices-speech
except Exception:
    speechsdk = None


# ---------------------------------------------------------------------------
# Demo 2: Model Deployment + Endpoint Test (Azure OpenAI via Foundry endpoint)
# ---------------------------------------------------------------------------
def demo_aoai_chat_completions() -> Dict[str, Any]:
    """
    Calls a deployed Azure OpenAI chat model (e.g., GPT‑4.1) using REST.
    Configure:
      - AZURE_OPENAI_ENDPOINT (e.g., https://<your-endpoint>.openai.azure.com/)
      - AZURE_OPENAI_KEY
      - AZURE_OPENAI_DEPLOYMENT (your deployment name in Foundry)
      - AZURE_OPENAI_API_VERSION (e.g., 2024-02-15-preview or newer)
    """
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("AZURE_OPENAI_KEY", "")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    assert endpoint and api_key and deployment, "Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT"

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "Hello from Azure AI Foundry – what can you do?"}
        ],
        "temperature": 0.2
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    print(json.dumps(data, indent=2))
    return data


# ---------------------------------------------------------------------------
# Demo 3: Service Endpoint – Speech‑to‑Text (Azure AI Speech)
# ---------------------------------------------------------------------------
def demo_speech_to_text(wav_path: str = "../data/audio/Recording.wav") -> str:
    """
    Transcribes a local WAV/MP3 file using Azure AI Speech SDK.
    Configure:
      - AZURE_SPEECH_KEY
      - AZURE_SPEECH_REGION
    """
    if speechsdk is None:
        raise RuntimeError("azure-cognitiveservices-speech not installed. pip install azure-cognitiveservices-speech")

    speech_key = os.environ.get("AZURE_SPEECH_KEY", "")
    speech_region = os.environ.get("AZURE_SPEECH_REGION", "")
    assert speech_key and speech_region, "Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION"

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    audio_config = speechsdk.AudioConfig(filename=wav_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Transcribing...")
    result = recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Transcript:", result.text)
        return result.text
    else:
        print("No speech recognized or an error occurred:", result.reason)
        return ""


# ---------------------------------------------------------------------------
# Demo 4: Service Endpoint – Translator (REST)
# ---------------------------------------------------------------------------
def demo_translator(text: str = "Good morning, welcome to the AI workshop", to_lang: str = "fr") -> List[Dict[str, Any]]:
    """
    Translates text using Azure Translator REST API.
    Configure:
      - AZURE_TRANSLATOR_KEY
      - AZURE_TRANSLATOR_REGION
    """
    translator_key = os.environ.get("AZURE_TRANSLATOR_KEY", "")
    translator_region = os.environ.get("AZURE_TRANSLATOR_REGION", "")
    assert translator_key and translator_region, "Set AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_REGION"

    url = f"https://api.cognitive.microsofttranslator.com/translate"
    params = {
        "api-version": "3.0",
        "to": to_lang,
    }
    headers = {
        "Ocp-Apim-Subscription-Key": translator_key,
        "Ocp-Apim-Subscription-Region": translator_region,
        "Content-Type": "application/json",
    }
    body = [{"text": text}]
    resp = requests.post(url, params=params, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


# ---------------------------------------------------------------------------
# Demo 5: Document Intelligence (Analyze) + Summarize via AOAI
# ---------------------------------------------------------------------------
def demo_document_intelligence_and_summarize(
    file_path: str = "../data/documents/TP25-40.pdf",
    model: str = "prebuilt-layout",
) -> Dict[str, Any]:
    """
    Uses Azure AI Document Intelligence Analyze REST API, then summarizes with Azure OpenAI.
    Configure:
      - AZURE_DOCINTEL_ENDPOINT (e.g., https://<resourcename>.cognitiveservices.azure.com/)
      - AZURE_DOCINTEL_KEY
      - Azure OpenAI env vars from demo_aoai_chat_completions for summarization step.

    Notes:
      - This uses the 2024-07-31 (or similar) Document Intelligence API version; update if needed.
      - For larger files, consider streaming upload or SAS URL.
    """
    docintel_endpoint = os.environ.get("AZURE_DOCINTEL_ENDPOINT", "").rstrip("/")
    docintel_key = os.environ.get("AZURE_DOCINTEL_KEY", "")
    assert docintel_endpoint and docintel_key, "Set AZURE_DOCINTEL_ENDPOINT and AZURE_DOCINTEL_KEY"

    # 1) Submit Analyze request (prebuilt model)
    analyze_url = f"{docintel_endpoint}/formrecognizer/documentModels/{model}:analyze?api-version=2024-07-31"
    headers = {
        "Ocp-Apim-Subscription-Key": docintel_key,
        "Content-Type": "application/pdf"
    }
    with open(file_path, "rb") as f:
        analyze_resp = requests.post(analyze_url, headers=headers, data=f, timeout=60)
    analyze_resp.raise_for_status()

    # 2) Get operation-location to poll for result
    op_location = analyze_resp.headers.get("operation-location")
    assert op_location, "No operation-location header returned"
    print("Analyze submitted. Polling for result...")

    # 3) Poll for completion
    for _ in range(30):
        poll = requests.get(op_location, headers={"Ocp-Apim-Subscription-Key": docintel_key}, timeout=60)
        poll.raise_for_status()
        result = poll.json()
        status = result.get("status", "").lower()
        print("Status:", status)
        if status in ("succeeded", "failed"):
            break
        time.sleep(2)

    if status != "succeeded":
        raise RuntimeError(f"Analyze did not succeed: {status}")

    # 4) Extract a concise JSON payload (first page summary)
    content = result.get("analyzeResult", {})
    # Keep it compact for the LLM prompt
    compact = {
        "pages": content.get("pages", []),
        "keyValuePairs": content.get("keyValuePairs", []),
        "tables": content.get("tables", []),
        "paragraphs": content.get("paragraphs", [])[:5],  # limit to a few
    }
    print("Doc Intelligence (compact):", json.dumps(compact, indent=2))

    # 5) Summarize with Azure OpenAI
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("AZURE_OPENAI_KEY", "")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    assert endpoint and api_key and deployment, "Set AOAI env vars for summarization step"

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    headers = {"Content-Type": "application/json", "api-key": api_key}
    prompt = (
        "Summarize the following document for a business stakeholder. "
        "Include who/what/when/amounts. Be concise:\n\n"
        f"{json.dumps(compact)[:12000]}"
    )
    payload = {"messages": [{"role": "user", "content": prompt}], "temperature": 0.2}
    aoai_resp = requests.post(url, headers=headers, json=payload, timeout=120)
    aoai_resp.raise_for_status()
    aoai_data = aoai_resp.json()
    print("Summary:", json.dumps(aoai_data, indent=2))
    return {"docintel": result, "summary": aoai_data}


# ---------------------------------------------------------------------------
# Utilities: minimal cURL examples (copy/paste into terminal)
# ---------------------------------------------------------------------------
CURL_AOAI_EXAMPLE = r'''
# Azure OpenAI chat completions via curl (replace placeholders)
curl -X POST "$AZURE_OPENAI_ENDPOINT/openai/deployments/$AZURE_OPENAI_DEPLOYMENT/chat/completions?api-version=$AZURE_OPENAI_API_VERSION"  -H "Content-Type: application/json"  -H "api-key: $AZURE_OPENAI_KEY"  -d '{ "messages": [{"role":"user","content":"Hello from curl"}], "temperature": 0.2 }'
'''

CURL_TRANSLATOR_EXAMPLE = r'''
# Azure Translator via curl (replace placeholders)
curl -X POST "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=fr"  -H "Ocp-Apim-Subscription-Key: $AZURE_TRANSLATOR_KEY"  -H "Ocp-Apim-Subscription-Region: $AZURE_TRANSLATOR_REGION"  -H "Content-Type: application/json"  -d '[{"text":"Good morning, welcome to the AI workshop"}]'
'''


if __name__ == "__main__":
    # Uncomment the demos you want to run locally after setting env vars.

    # 1) Azure OpenAI chat completions via Foundry endpoint
    # demo_aoai_chat_completions()

    # 2) Speech-to-Text (requires azure-cognitiveservices-speech and sample.wav)
    # demo_speech_to_text("sample.wav")

    # 3) Translator demo
    # demo_translator("Good morning, welcome to the AI workshop", "fr")

    # 4) Document Intelligence + Summarize
    # demo_document_intelligence_and_summarize("sample.pdf", model="prebuilt-layout")

    # Print handy cURL snippets
    print("---- Handy cURL snippets (copy/paste, then replace placeholders) ----")
    print(CURL_AOAI_EXAMPLE)
    print(CURL_TRANSLATOR_EXAMPLE)
