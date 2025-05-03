'''
The following code uses Google Gemini API for text completion. 
Call parameters:
prompt - text for completion
Function returns:
string - response prediction or error message
'''
import os
import google.generativeai as genai

api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

def call_gemini(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini error:", e)
        return "Sorry, I couldn't generate a response."
