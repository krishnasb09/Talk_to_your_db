"""
List available Gemini models for the provided API key.
"""
import os
import google.generativeai as genai

api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    # Try to grab from user input if not in env
    try:
        api_key = input("Enter API Key: ")
    except:
        pass

if not api_key:
    print("No API key provided.")
    exit(1)

genai.configure(api_key=api_key)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
