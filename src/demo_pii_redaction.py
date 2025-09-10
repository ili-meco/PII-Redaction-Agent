#!/usr/bin/env python3
"""
demo_pii_redaction.py
Quick demo of the PII redaction agent
"""

import os
import sys
sys.path.append('..')
from pii_redaction_agent import PIIRedactionAgent
from env_loader import load_dotenv

def main():
    load_dotenv('../config/.env')
    
    print("PII Redaction Agent Demo")
    print("="*50)
    
    # Use the existing receipt.png file for demo
    input_file = "../data/images/receipt.png"
    
    if not os.path.exists(input_file):
        print(f"Demo file '{input_file}' not found!")
        print("Available files for testing:")
        for file in os.listdir("../data/images"):
            if file.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                print(f"  - {file}")
        return
    
    try:
        # Initialize the agent
        agent = PIIRedactionAgent()
        
        # Process the document
        result = agent.process_document(input_file, "../results/pii_detection/redacted_text/receipt_redacted.txt")
        
        print("\nDemo completed successfully!")
        print(f"Check the file: {result.redacted_file}")
        
    except Exception as e:
        print(f"Demo failed: {e}")

if __name__ == "__main__":
    main()
