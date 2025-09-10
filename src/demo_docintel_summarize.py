#!/usr/bin/env python3
# demo_docintel_summarize.py
# Analyze a PDF with Azure AI Document Intelligence, then summarize via Azure OpenAI.
import os, json, time, requests
from env_loader import load_dotenv

def analyze_document(file_path: str, model: str, endpoint: str, key: str):
    # Try a more stable API version
    url = f"{endpoint.rstrip('/')}/formrecognizer/documentModels/{model}:analyze?api-version=2023-07-31"
    
    # Determine content type based on file extension
    content_type = "application/pdf"
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        content_type = "image/jpeg"
    elif file_path.lower().endswith('.tiff'):
        content_type = "image/tiff"
    
    headers = {"Ocp-Apim-Subscription-Key": key, "Content-Type": content_type}
    print(f"Analyzing {file_path} with endpoint: {url}")
    print(f"Content-Type: {content_type}")
    
    with open(file_path, "rb") as f:
        r = requests.post(url, headers=headers, data=f, timeout=60)
    
    if not r.ok:
        print(f"Error {r.status_code}: {r.text}")
        print(f"Request URL: {url}")
        print(f"Headers: {headers}")
    
    r.raise_for_status()
    op = r.headers.get("operation-location")
    if not op:
        raise RuntimeError("No operation-location header returned")
    for _ in range(30):
        poll = requests.get(op, headers={"Ocp-Apim-Subscription-Key": key}, timeout=60)
        poll.raise_for_status()
        data = poll.json()
        status = data.get("status","").lower()
        print("Status:", status)
        if status in ("succeeded","failed"):
            return data
        time.sleep(2)
    raise RuntimeError("Timeout polling analyze operation")

def summarize_with_aoai(summary_input: dict) -> dict:
    aoai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT","").rstrip("/")
    aoai_key = os.environ.get("AZURE_OPENAI_KEY","")
    aoai_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT","")
    aoai_version = os.environ.get("AZURE_OPENAI_API_VERSION","2024-02-15-preview")
    assert aoai_endpoint and aoai_key and aoai_deployment, "Set Azure OpenAI vars in .env"
    url = f"{aoai_endpoint}/openai/deployments/{aoai_deployment}/chat/completions?api-version={aoai_version}"
    headers = {"Content-Type":"application/json","api-key":aoai_key}
    compact = {
        "pages": summary_input.get("analyzeResult",{}).get("pages",[]),
        "keyValuePairs": summary_input.get("analyzeResult",{}).get("keyValuePairs",[]),
        "tables": summary_input.get("analyzeResult",{}).get("tables",[]),
        "paragraphs": summary_input.get("analyzeResult",{}).get("paragraphs",[])[:5],
    }
    prompt = (
        "Summarize the following document for a business stakeholder. "
        "Include who/what/when/amounts. Be concise:\n\n"
        + json.dumps(compact)[:12000]
    )
    payload = {"messages":[{"role":"user","content":prompt}],"temperature":0.2}
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()

def main():
    load_dotenv()
    di_endpoint = os.environ.get("AZURE_DOCINTEL_ENDPOINT","")
    di_key = os.environ.get("AZURE_DOCINTEL_KEY","")
    pdf = os.environ.get("DOCINTEL_FILE","../data/images/receipt.png")
    model = os.environ.get("DOCINTEL_MODEL","prebuilt-layout")
    assert di_endpoint and di_key, "Set AZURE_DOCINTEL_ENDPOINT and AZURE_DOCINTEL_KEY in .env"

    print("Analyzing:", pdf)
    analysis = analyze_document(pdf, model, di_endpoint, di_key)
    print("Analyze complete.")
    summary = summarize_with_aoai(analysis)
    print(json.dumps({"docintel": analysis, "summary": summary}, indent=2))

if __name__ == "__main__":
    main()
