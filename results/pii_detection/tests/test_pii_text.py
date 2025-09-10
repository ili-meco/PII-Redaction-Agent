#!/usr/bin/env python3
"""
test_pii_text.py
Test the PII detection on plain text files
"""

import os
import json
import sys

# Add the src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from pii_redaction_agent import PIIRedactionAgent
from env_loader import load_dotenv

def test_text_pii_detection():
    """Test PII detection on a plain text file"""
    load_dotenv('../../../config/.env')
    
    print("Testing PII Detection on Text")
    print("="*50)
    
    # Read the sample text file from the new location
    text_file = "../../../data/documents/sample_document_with_pii.txt"
    if not os.path.exists(text_file):
        print(f"Test file '{text_file}' not found!")
        return
    
    with open(text_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    try:
        # Initialize agent
        agent = PIIRedactionAgent()
        
        print(f"Analyzing text ({len(text_content)} characters)...")
        
        # Test AI-based PII detection
        print("\nAI-based PII detection:")
        ai_entities = agent.detect_pii_with_ai(text_content)
        for entity in ai_entities:
            print(f"  - {entity.pii_type.value}: '{entity.text}' (confidence: {entity.confidence})")
        
        # Test regex-based detection
        print("\nRegex-based PII detection:")
        regex_entities = agent.apply_regex_patterns(text_content)
        for entity in regex_entities:
            print(f"  - {entity.pii_type.value}: '{entity.text}' (confidence: {entity.confidence})")
        
        # Create redacted version
        all_entities = ai_entities + regex_entities
        # Simple deduplication
        unique_entities = []
        for entity in all_entities:
            is_duplicate = False
            for existing in unique_entities:
                if (abs(entity.start_position - existing.start_position) < 5):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_entities.append(entity)
        
        print(f"\nTotal unique PII entities found: {len(unique_entities)}")
        
        # Create redacted text
        redacted_text = agent.create_redacted_text(text_content, unique_entities)
        
        # Save redacted version
        output_file = "../redacted_text/sample_document_redacted.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(redacted_text)
        
        print(f"Redacted version saved: {output_file}")
        
        # Generate report
        report = agent.generate_redaction_report(unique_entities)
        
        print("\nRedaction Summary:")
        print(json.dumps(report, indent=2))
        
        # Save report
        with open("../reports/sample_document_pii_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print("\nPII detection test completed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    test_text_pii_detection()
