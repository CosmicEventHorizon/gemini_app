import json
import os

FAQ_PATH = 'data/faq.json'

def read_faq_from_file():
    try:
        with open(FAQ_PATH, 'r') as file:
            questions = json.load(file)
        return questions
    except Exception as e:
        print(f"Error reading questions file: {e}")
        return {}