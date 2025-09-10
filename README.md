# Azure AI Foundry – Day 1 Demos

# PII Redaction Agent - Azure AI Workshop

An intelligent agent that detects and redacts Personally Identifiable Information (PII) from documents using Azure Document Intelligence and Azure OpenAI.

## 🎯 Features

- **Multi-layered PII Detection**: Combines AI-powered detection with regex pattern backup
- **Document Analysis**: Supports PDF, images (PNG, JPG, JPEG) using Azure Document Intelligence
- **Bounding Box Mapping**: Visual location coordinates for redacted content
- **Comprehensive Reporting**: JSON reports with confidence scores and detailed analysis
- **Enterprise-ready**: Professional output suitable for business use
- **Self-contained Module**: Complete organization with source code, tests, and outputs

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Azure subscription with the following services:
  - Azure OpenAI Service
  - Azure Document Intelligence
  - Azure Speech Services (optional)
  - Azure Translator (optional)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd pii-redaction-workshop
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Azure services**
```bash
# Copy the environment template
cp .env.template config/.env

# Edit config/.env with your Azure credentials
```

4. **Test the setup**
```bash
# Navigate to the PII detection module
cd results/pii_detection/src

# Run the demo
python demo_pii_redaction.py
```

## 📋 Configuration

Edit `config/.env` with your Azure service credentials:

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Azure Document Intelligence
AZURE_DOCINTEL_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCINTEL_KEY=your-document-intelligence-key

# Optional: Azure Speech Services
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=your-region

# Optional: Azure Translator
AZURE_TRANSLATOR_KEY=your-translator-key
AZURE_TRANSLATOR_REGION=your-region
```

## 🔧 Usage

### Quick Demo
```bash
cd results/pii_detection/src
python demo_pii_redaction.py
```

### Command Line Interface
```bash
cd results/pii_detection/src
python pii_redaction_agent.py --file ../../../data/images/driverslicense.jpg
python pii_redaction_agent.py --file ../../../data/documents/sample_document.pdf --output custom_output.txt
```

### Text-based Testing
```bash
cd results/pii_detection/tests
python test_pii_text.py
```

## 📁 Project Structure

```
├── config/                     # Configuration files
│   └── .env                    # Azure credentials (create from template)
├── data/                       # Sample input files
│   ├── audio/                  # Audio samples
│   ├── documents/              # Text documents
│   └── images/                 # Image samples
├── results/pii_detection/      # Self-contained PII module
│   ├── src/                    # Source code
│   ├── tests/                  # Unit tests
│   ├── redacted_text/          # Output redacted files
│   └── reports/                # Analysis reports
└── src/                        # Other Azure AI demos
```

## 🎓 Workshop Activities

### Activity 1: Basic PII Detection
1. Run the demo with sample images
2. Examine the redacted output
3. Review the confidence scores

### Activity 2: Custom Document Processing
1. Add your own documents to `data/documents/`
2. Process with the CLI tool
3. Analyze the generated reports

### Activity 3: Bounding Box Analysis
1. Process image documents
2. Examine bounding box coordinates
3. Understand visual redaction possibilities

## 🔍 Detected PII Types

- Social Security Numbers
- Email Addresses  
- Phone Numbers
- Physical Addresses
- Credit Card Numbers
- Driver License Numbers
- Names
- Dates of Birth
- IP Addresses
- Bank Account Numbers

## 📊 Output Files

- **Redacted Text**: Clean documents with PII removed
- **JSON Reports**: Detailed analysis with confidence scores
- **Bounding Box Data**: Visual coordinates for image-based redaction

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify Azure credentials in `config/.env`
   - Check service endpoint URLs
   - Ensure proper API versions

2. **Module Import Errors**
   - Run commands from the correct directory
   - Verify Python path configuration

3. **File Not Found**
   - Check relative paths from execution directory
   - Ensure sample files exist in `data/` folders

### Getting Help

- Check the console output for detailed error messages
- Verify Azure service quotas and limits
- Review the sample files for expected formats

## 🎯 Learning Objectives

By the end of this workshop, you will:

- Understand multi-layered PII detection approaches
- Know how to integrate Azure AI services for document processing
- Be able to implement enterprise-grade data protection
- Understand confidence scoring and validation techniques
- Have hands-on experience with Azure Document Intelligence and OpenAI

## 📝 License

This project is provided for educational purposes as part of the Azure AI workshop.

## 🤝 Contributing

This is a workshop repository. For questions or improvements, please reach out to the workshop facilitator.

## Files
- `env_loader.py` – tiny .env loader (no external dependency).
- `demo_aoai_chat.py` – call your Azure OpenAI deployment endpoint.
- `demo_speech_to_text.py` – Azure Speech-to-Text for a local audio file.
- `demo_translator.py` – Azure Translator REST call.
- `demo_docintel_summarize.py` – Document Intelligence analyze, then summarize with AOAI.
- `.env.example` – copy to `.env` and fill in.

## Setup
1. Python 3.10+
2. `pip install requests azure-cognitiveservices-speech` (install Speech SDK only if you plan to run the speech demo)
3. Place `sample.wav` (for speech) and `sample.pdf` (for doc intelligence) in this folder.
4. Copy `.env.example` to `.env` and fill in values.

## Run
```bash
python demo_aoai_chat.py
python demo_speech_to_text.py      # requires sample.wav
python demo_translator.py
python demo_docintel_summarize.py  # requires sample.pdf
```
