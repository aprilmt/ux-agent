#!/usr/bin/env python3
"""
Setup script for OpenAI API key
"""

import os

def setup_api_key():
    print("🔑 OpenAI API Key Setup")
    print("=" * 50)
    print("To use the LLM-powered UX AI Agent, you need an OpenAI API key.")
    print("You can get one from: https://platform.openai.com/api-keys")
    print()
    
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file
        with open('.env', 'r') as f:
            content = f.read()
        
        content = content.replace('OPENAI_API_KEY=your_openai_api_key_here', f'OPENAI_API_KEY={api_key}')
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print("✅ API key saved to .env file")
        return True
    else:
        print("⚠️  Skipping API key setup. You can set it later in the .env file.")
        return False

if __name__ == "__main__":
    setup_api_key()
