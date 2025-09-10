#!/usr/bin/env python3
# demo_aoai_chat.py
# Azure OpenAI chat completions via your Foundry deployment endpoint.
import os, json, requests
from env_loader import load_dotenv

def main():
    load_dotenv()
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("AZURE_OPENAI_KEY", "")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    assert endpoint and api_key and deployment, "Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT in .env"

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    headers = {"Content-Type":"application/json","api-key":api_key}
    payload = {
        "messages":[
            {"role":"system","content":"You are a concise assistant."},
            {"role":"user","content":"Hello from Azure AI Foundry – what can you do?"}
        ],
        "temperature":0.2
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    main()
