# src/llm.py
import google.generativeai as genai
import os
# CHANGE: Import from src.config
from src.config import GEMINI_API_KEY, GEMINI_MODEL


genai.configure(api_key=GEMINI_API_KEY)

def chat_with_llm(messages):
    """
    messages: list of strings.
    We join them into a single context block to avoid API schema errors.
    """
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    # FIX: Join the history list into a single string prompt
    full_prompt = "\n\n".join(messages)
    
    try:
        response = model.generate_content(
            full_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return response.text
    except Exception as e:
        # Fallback for safety
        return f'{{"thought": "LLM Error: {str(e)}", "action": "stop"}}'