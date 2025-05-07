import os
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def call_openai(prompt: str):
    try:
        response = client.responses.create(
            model="gpt-4.1-nano",
            input=prompt,
            temperature=0.8,
            top_p=0.9,
        )
        return response.output_text
    except Exception as e:
        print("OpenAI error:", e)
        return "Sorry, I couldn't generate a response."
