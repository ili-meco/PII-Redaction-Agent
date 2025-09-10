#!/usr/bin/env python3
"""
pii_redaction_agent.py
-----------------------
An intelligent agent that detects and redacts PII (Personally Identifiable Information) 
from documents using Azure Document Intelligence and Azure OpenAI.

Features:
- Analyzes documents with Azure Document Intelligence
- Uses Azure OpenAI to identify PII entities
- Creates redacted versions of documents
- Supports multiple PII types (SSN, email, phone, address, etc.)
- Generates redaction reports

Usage:
    python pii_redaction_agent.py --file document.pdf --output redacted_document.pdf
"""

import os
import sys
import json
import time
import re
import argparse
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import requests

# Add the current directory to path for env_loader
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from env_loader import load_dotenv

class PIIType(Enum):
    """Types of PII that can be detected and redacted"""
    SSN = "Social Security Number"
    EMAIL = "Email Address"
    PHONE = "Phone Number" 
    ADDRESS = "Physical Address"
    CREDIT_CARD = "Credit Card Number"
    NAME = "Person Name"
    DATE_OF_BIRTH = "Date of Birth"
    DRIVER_LICENSE = "Driver License"
    PASSPORT = "Passport Number"
    BANK_ACCOUNT = "Bank Account Number"
    IP_ADDRESS = "IP Address"
    URL = "URL"

@dataclass
class PIIEntity:
    """Represents a detected PII entity"""
    text: str
    pii_type: PIIType
    confidence: float
    start_position: int
    end_position: int
    page_number: int = None
    bounding_box: Dict = None

@dataclass
class RedactionResult:
    """Results of the redaction process"""
    original_file: str
    redacted_file: str
    pii_entities: List[PIIEntity]
    redaction_summary: Dict[str, int]
    timestamp: str

class PIIRedactionAgent:
    """Main agent class for PII detection and redaction"""
    
    def __init__(self):
        load_dotenv()
        self.docintel_endpoint = os.environ.get("AZURE_DOCINTEL_ENDPOINT", "").rstrip("/")
        self.docintel_key = os.environ.get("AZURE_DOCINTEL_KEY", "")
        self.aoai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        self.aoai_key = os.environ.get("AZURE_OPENAI_KEY", "")
        self.aoai_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
        self.aoai_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        # Validate configuration
        assert self.docintel_endpoint and self.docintel_key, "Set AZURE_DOCINTEL_ENDPOINT and AZURE_DOCINTEL_KEY"
        assert self.aoai_endpoint and self.aoai_key and self.aoai_deployment, "Set Azure OpenAI environment variables"
        
        print("PII Redaction Agent initialized")
        print(f"Document Intelligence: {self.docintel_endpoint[:50]}...")
        print(f"Azure OpenAI: {self.aoai_deployment}")

    def analyze_document(self, file_path: str, model: str = "prebuilt-layout") -> Dict[str, Any]:
        """Analyze document with Azure Document Intelligence"""
        print(f"Analyzing document: {file_path}")
        
        url = f"{self.docintel_endpoint}/formrecognizer/documentModels/{model}:analyze?api-version=2023-07-31"
        
        # Determine content type
        content_type = "application/pdf"
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            content_type = "image/jpeg"
        elif file_path.lower().endswith('.tiff'):
            content_type = "image/tiff"
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.docintel_key,
            "Content-Type": content_type
        }
        
        with open(file_path, "rb") as f:
            response = requests.post(url, headers=headers, data=f, timeout=60)
        
        if not response.ok:
            print(f"Document Intelligence error {response.status_code}: {response.text}")
            response.raise_for_status()
        
        # Poll for results
        operation_location = response.headers.get("operation-location")
        if not operation_location:
            raise RuntimeError("No operation-location header returned")
        
        print("Waiting for analysis to complete...")
        for i in range(30):
            poll_response = requests.get(
                operation_location, 
                headers={"Ocp-Apim-Subscription-Key": self.docintel_key}, 
                timeout=60
            )
            poll_response.raise_for_status()
            result = poll_response.json()
            status = result.get("status", "").lower()
            
            if status == "succeeded":
                print("Document analysis complete")
                return result
            elif status == "failed":
                raise RuntimeError(f"Document analysis failed: {result}")
            
            print(f"Status: {status} ({i+1}/30)")
            time.sleep(2)
        
        raise RuntimeError("Timeout waiting for document analysis")

    def extract_text_content(self, analysis_result: Dict[str, Any]) -> str:
        """Extract all text content from document analysis"""
        analyze_result = analysis_result.get("analyzeResult", {})
        
        # Extract text from paragraphs (preferred method)
        paragraphs = analyze_result.get("paragraphs", [])
        if paragraphs:
            text_content = "\n".join([p.get("content", "") for p in paragraphs])
        else:
            # Fallback: extract from pages
            pages = analyze_result.get("pages", [])
            text_content = ""
            for page in pages:
                lines = page.get("lines", [])
                page_text = "\n".join([line.get("content", "") for line in lines])
                text_content += page_text + "\n"
        
        return text_content.strip()

    def detect_pii_with_ai(self, text_content: str) -> List[PIIEntity]:
        """Use Azure OpenAI to detect PII entities in text"""
        print("Analyzing text for PII with Azure OpenAI...")
        
        prompt = f"""
You are a PII (Personally Identifiable Information) detection expert. Analyze the following text and identify ALL PII entities.

For each PII entity found, provide:
1. The exact text of the PII
2. The type of PII (SSN, EMAIL, PHONE, ADDRESS, CREDIT_CARD, NAME, DATE_OF_BIRTH, DRIVER_LICENSE, PASSPORT, BANK_ACCOUNT, IP_ADDRESS, URL)
3. Confidence level (0.0 to 1.0)
4. Start and end character positions in the text

Return ONLY a JSON array with this format:
[
  {{
    "text": "exact PII text",
    "pii_type": "PII_TYPE",
    "confidence": 0.95,
    "start_position": 123,
    "end_position": 135
  }}
]

Text to analyze:
{text_content}
"""

        url = f"{self.aoai_endpoint}/openai/deployments/{self.aoai_deployment}/chat/completions?api-version={self.aoai_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.aoai_key
        }
        payload = {
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert PII detection system. Return only valid JSON arrays."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        ai_response = response.json()
        ai_content = ai_response["choices"][0]["message"]["content"].strip()
        
        # Extract JSON from response
        try:
            # Remove code block markers if present
            if "```json" in ai_content:
                ai_content = ai_content.split("```json")[1].split("```")[0]
            elif "```" in ai_content:
                ai_content = ai_content.split("```")[1].split("```")[0]
            
            pii_data = json.loads(ai_content)
            
            # Convert to PIIEntity objects
            pii_entities = []
            for item in pii_data:
                try:
                    pii_type = PIIType(item["pii_type"])
                except ValueError:
                    # Handle unknown PII types
                    continue
                
                entity = PIIEntity(
                    text=item["text"],
                    pii_type=pii_type,
                    confidence=item["confidence"],
                    start_position=item["start_position"],
                    end_position=item["end_position"]
                )
                pii_entities.append(entity)
            
            print(f"Found {len(pii_entities)} PII entities")
            return pii_entities
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {e}")
            print(f"Response: {ai_content}")
            return []

    def apply_regex_patterns(self, text: str) -> List[PIIEntity]:
        """Apply regex patterns for common PII types as backup detection"""
        patterns = {
            PIIType.SSN: r'\b\d{3}-?\d{2}-?\d{4}\b',
            PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            PIIType.PHONE: r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            PIIType.CREDIT_CARD: r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            PIIType.IP_ADDRESS: r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        }
        
        regex_entities = []
        for pii_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = PIIEntity(
                    text=match.group(),
                    pii_type=pii_type,
                    confidence=0.8,  # High confidence for regex matches
                    start_position=match.start(),
                    end_position=match.end()
                )
                regex_entities.append(entity)
        
        return regex_entities

    def create_redacted_text(self, original_text: str, pii_entities: List[PIIEntity]) -> str:
        """Create redacted version of text"""
        redacted_text = original_text
        
        # Sort entities by position (reverse order to maintain positions)
        sorted_entities = sorted(pii_entities, key=lambda x: x.start_position, reverse=True)
        
        for entity in sorted_entities:
            # Create redaction placeholder
            redaction = f"[REDACTED-{entity.pii_type.name}]"
            
            # Replace the PII text
            redacted_text = (
                redacted_text[:entity.start_position] + 
                redaction + 
                redacted_text[entity.end_position:]
            )
        
        return redacted_text

    def generate_redaction_report(self, pii_entities: List[PIIEntity]) -> Dict[str, Any]:
        """Generate a summary report of redactions"""
        summary = {}
        
        # Count by PII type
        for entity in pii_entities:
            pii_type_name = entity.pii_type.value
            summary[pii_type_name] = summary.get(pii_type_name, 0) + 1
        
        total_redactions = len(pii_entities)
        avg_confidence = sum(e.confidence for e in pii_entities) / total_redactions if total_redactions > 0 else 0
        
        return {
            "total_redactions": total_redactions,
            "average_confidence": round(avg_confidence, 3),
            "by_type": summary,
            "entities": [
                {
                    "text": "***REDACTED***",  # Don't include actual PII in report
                    "type": entity.pii_type.value,
                    "confidence": entity.confidence,
                    "position": f"{entity.start_position}-{entity.end_position}"
                }
                for entity in pii_entities
            ]
        }

    def process_document(self, input_file: str, output_file: str = None) -> RedactionResult:
        """Main method to process a document for PII redaction"""
        if not output_file:
            name, ext = os.path.splitext(os.path.basename(input_file))
            # Determine if it's an image or document to choose the right subfolder
            if input_file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                output_file = f"../redacted_text/{name}_redacted.txt"
            else:
                output_file = f"../redacted_text/{name}_redacted.txt"
        
        print(f"Starting PII redaction for: {input_file}")
        
        # Step 1: Analyze document with Document Intelligence
        analysis_result = self.analyze_document(input_file)
        
        # Step 2: Extract text content
        text_content = self.extract_text_content(analysis_result)
        print(f"Extracted {len(text_content)} characters of text")
        
        # Step 3: Detect PII with AI
        ai_entities = self.detect_pii_with_ai(text_content)
        
        # Step 4: Apply regex patterns as backup
        regex_entities = self.apply_regex_patterns(text_content)
        
        # Step 5: Combine and deduplicate entities
        all_entities = ai_entities + regex_entities
        # Simple deduplication based on position overlap
        unique_entities = []
        for entity in all_entities:
            is_duplicate = False
            for existing in unique_entities:
                if (abs(entity.start_position - existing.start_position) < 5 and 
                    abs(entity.end_position - existing.end_position) < 5):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_entities.append(entity)
        
        print(f"Final count: {len(unique_entities)} unique PII entities detected")
        
        # Step 6: Create redacted text
        redacted_text = self.create_redacted_text(text_content, unique_entities)
        
        # Step 7: Save redacted document
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(redacted_text)
        
        print(f"Redacted document saved: {output_file}")
        
        # Step 8: Generate report
        report = self.generate_redaction_report(unique_entities)
        
        # Step 9: Auto-save report to reports folder
        name, ext = os.path.splitext(os.path.basename(input_file))
        report_file = f"../reports/{name}_pii_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved: {report_file}")
        
        result = RedactionResult(
            original_file=input_file,
            redacted_file=output_file,
            pii_entities=unique_entities,
            redaction_summary=report,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return result

def main():
    """CLI interface for the PII redaction agent"""
    parser = argparse.ArgumentParser(description="Redact PII from documents using Azure AI")
    parser.add_argument("--file", "-f", required=True, help="Input document file path")
    parser.add_argument("--output", "-o", help="Output file path (optional)")
    parser.add_argument("--report", "-r", help="Save redaction report to JSON file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        return
    
    try:
        # Initialize agent
        agent = PIIRedactionAgent()
        
        # Process document
        result = agent.process_document(args.file, args.output)
        
        # Print summary
        print("\n" + "="*60)
        print("REDACTION SUMMARY")
        print("="*60)
        print(f"Original file: {result.original_file}")
        print(f"Redacted file: {result.redacted_file}")
        print(f"Total redactions: {result.redaction_summary['total_redactions']}")
        print(f"Average confidence: {result.redaction_summary['average_confidence']}")
        print("\nRedactions by type:")
        for pii_type, count in result.redaction_summary['by_type'].items():
            print(f"  - {pii_type}: {count}")
        
        # Save report if requested
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(result.redaction_summary, f, indent=2)
            print(f"\nDetailed report saved: {args.report}")
        
        print(f"\nPII redaction completed successfully!")
        
    except Exception as e:
        print(f"Error during PII redaction: {e}")
        raise

if __name__ == "__main__":
    main()
