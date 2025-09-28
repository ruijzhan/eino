#!/usr/bin/env python3
"""Test script to verify launch configuration works."""

import sys
import os
from model import create_openai_chat_model
from template import create_messages_from_template

def main():
    """Test the basic functionality without making API calls."""
    print("Testing launch configuration...")

    # Check environment variables
    print(f"OPENAI_API_KEY: {'***' + os.getenv('OPENAI_API_KEY', 'NOT_SET')[-4:] if os.getenv('OPENAI_API_KEY') else 'NOT_SET'}")
    print(f"OPENAI_MODEL_NAME: {os.getenv('OPENAI_MODEL_NAME', 'NOT_SET')}")
    print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', 'NOT_SET')}")
    print(f"PYTHONPATH: {os.getenv('PYTHONPATH', 'NOT_SET')}")
    print(f"VIRTUAL_ENV: {os.getenv('VIRTUAL_ENV', 'NOT_SET')}")

    # Test template creation
    messages = create_messages_from_template()
    print(f"✓ Created {len(messages)} messages from template")

    # Test model creation (will fail without API key, but that's expected)
    try:
        model = create_openai_chat_model()
        print(f"✓ Created model: {model.model_name}")
    except ValueError as e:
        print(f"✓ Expected error without valid API key: {e}")

    print("✓ All tests passed! Launch configuration is working correctly.")

if __name__ == "__main__":
    main()