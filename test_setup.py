import os
from dotenv import load_dotenv
import anthropic
import requests

load_dotenv()

# Test API keys are loaded
print("Testing API keys...")
print(f"Anthropic API Key: {'✓ Found' if os.getenv('ANTHROPIC_API_KEY') else '✗ Missing'}")
print(f"Alpha Vantage API Key: {'✓ Found' if os.getenv('ALPHA_VANTAGE_API_KEY') else '✗ Missing'}")
print(f"News API Key: {'✓ Found' if os.getenv('NEWS_API_KEY') else '✗ Missing'}")

print("\nAll set! Ready to build. 🚀")