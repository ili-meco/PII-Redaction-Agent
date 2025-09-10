#!/usr/bin/env python3
# demo_translator.py
# Translate a sentence using Azure Translator REST API.
import os, json, requests
from env_loader import load_dotenv

def main():
    load_dotenv()
    key = os.environ.get("AZURE_TRANSLATOR_KEY", "")
    region = os.environ.get("AZURE_TRANSLATOR_REGION", "")
    text = os.environ.get("TRANSLATE_TEXT", "Good morning, welcome to the AI workshop")
    to_lang = os.environ.get("TRANSLATE_TO", "fr")
    assert key and region, "Set AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_REGION in .env"

    url = "https://api.cognitive.microsofttranslator.com/translate"
    params = {"api-version":"3.0","to":to_lang}
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-Type":"application/json"
    }
    body = [{"text": text}]
    resp = requests.post(url, params=params, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

# Translation Confidence Score Interpretation:
# 0.9 - 1.0: Very high confidence (excellent translation)
# 0.7 - 0.89: High confidence (good translation)
# 0.5 - 0.69: Moderate confidence (acceptable translation)
# 0.3 - 0.49: Low confidence (questionable translation)
# 0.0 - 0.29: Very low confidence (poor translation)

