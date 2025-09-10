# Azure AI Foundry Demo - Workspace Structure

This workspace is organized for the Azure AI Foundry demonstration with a clean, professional structure.

## Directory Structure

```
c:\DND-demo\
├── config/                     # Configuration files
│   └── .env                    # Environment variables and Azure credentials
├── data/                       # Input data and test files
│   ├── audio/                  # Audio files for speech recognition
│   │   └── Recording.wav
│   ├── documents/              # Text documents for PII detection
│   │   ├── sample_document_with_pii.txt
│   │   └── TP25-40.pdf
│   └── images/                 # Images for Document Intelligence
│       ├── driverslicense.jpg
│       └── receipt.png
├── results/                    # Output and generated files
│   └── pii_detection/          # Complete PII redaction module (self-contained)
│       ├── documents/          # Results from document-based PII detection
│       ├── images/             # Results from image-based PII detection  
│       ├── redacted_text/      # All redacted text output files
│       │   ├── driverslicense_redacted.txt
│       │   ├── receipt_redacted.txt
│       │   └── sample_document_redacted.txt
│       ├── reports/            # All JSON reports and analysis
│       │   ├── driverslicense_bounding_box_report.json
│       │   ├── driverslicense_pii_report.json
│       │   ├── pii_redaction_report.json
│       │   ├── receipt_bounding_box_report.json
│       │   ├── receipt_pii_report.json
│       │   └── sample_document_pii_report.json
│       ├── src/                # PII redaction source code
│       │   ├── demo_pii_redaction.py      # PII redaction demo
│       │   ├── env_loader.py              # Environment configuration
│       │   └── pii_redaction_agent.py     # Main PII detection agent
│       └── tests/              # PII redaction tests
│           └── test_pii_text.py           # Text-based PII testing
├── src/                        # Source code and demos (main Azure AI services)
│   ├── demo.py                 # Main comprehensive demo
│   ├── demo_aoai_chat.py       # Azure OpenAI chat demo
│   ├── demo_docintel_summarize.py  # Document Intelligence demo
│   ├── demo_speech_to_text_new.py  # Speech-to-text demo
│   ├── demo_translator.py      # Azure Translator demo
│   └── env_loader.py           # Environment configuration utility
├── tests/                      # Test scripts (general)
└── .env.template               # Template for environment variables
└── README.md                   # Project documentation
```

## Key Features

### Clean Organization
- **config/**: Centralized configuration management
- **data/**: Organized input data by type (audio, documents, images)
- **results/**: Structured output files by functionality
  - **pii_detection/**: Organized PII redaction results
    - **redacted_text/**: All redacted documents in one place
    - **reports/**: All analysis reports and bounding box data
    - **documents/**: Reserved for document-specific results
    - **images/**: Reserved for image-specific results
- **src/**: Professional source code organization
- **tests/**: Dedicated testing environment

### Azure AI Services Integration
- **Azure OpenAI**: GPT-4.1 deployment for intelligent PII detection
- **Azure Document Intelligence**: Layout analysis with bounding box extraction
- **Azure Speech Services**: Speech-to-text transcription
- **Azure Translator**: Multi-language translation capabilities

### Advanced PII Redaction
- **Multi-layered Detection**: AI-powered + regex pattern backup
- **Bounding Box Mapping**: Visual location coordinates for redacted content
- **Comprehensive Reporting**: JSON reports with confidence scores
- **Enterprise-ready**: Professional, emoji-free output for business use

## Usage

### Running PII Redaction (Self-contained module)
```bash
# From results/pii_detection/src/ directory
python demo_pii_redaction.py                    # Quick PII demo
python pii_redaction_agent.py --file ../../../data/images/driverslicense.jpg  # CLI interface

# From results/pii_detection/tests/ directory  
python test_pii_text.py                         # Text-based PII detection test
```

### Running Other Azure AI Demos
```bash
# From src/ directory
python demo.py                                  # Comprehensive Azure AI demo
python demo_aoai_chat.py                        # Azure OpenAI chat
python demo_speech_to_text_new.py               # Speech recognition
python demo_translator.py                       # Translation service
python demo_docintel_summarize.py               # Document Intelligence
```

### Configuration
- Copy `.env.template` to `config/.env`
- Fill in your Azure service credentials
- All demos automatically use the centralized configuration
