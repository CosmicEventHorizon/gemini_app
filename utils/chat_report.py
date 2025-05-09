import json
import os
from flask import jsonify
from retriever.search import get_relevant_chunks
from utils.model import call_openai
from utils.console import clear_terminal

CONVERSATION_DIR = "data/conversations"
os.makedirs(CONVERSATION_DIR, exist_ok=True)

def get_conversation_file(username):
    return os.path.join(CONVERSATION_DIR, f"user_{username}_report_history.json")

def load_conversation(username):
    file_path = get_conversation_file(username)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {"conversation": [], "context": []}

def save_conversation(username, data):
    file_path = get_conversation_file(username)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def add_message(username, message):
    data = load_conversation(username)
    print(data)
    data["conversation"].append({
        "message": message,
    })
    save_conversation(username, data)

def add_context(username, context):
    data = load_conversation(username)
    data["context"].append({
        "context": context,
    })
    save_conversation(username, data)

def query_messages(username):
    data = load_conversation(username)
    result = {
        "conversation": [],
        "context": []
    }
    result['conversation'] = '\n\n'.join(m['message'] for m in data['conversation'][-10:])
    result['context'] = '\n'.join(c['context'] for c in data['context'][-3:])
    return result

def handle_report_chat(prompt, report_name, username):
    relevant_context = get_relevant_chunks(prompt, report_name, 15)
    if relevant_context is None: 
        return jsonify({"response": "Please reload the database"}) 

    user_prompt = "User: " + prompt
    
    add_message(
        username=username,
        message=user_prompt,
    )

    add_context(
        username=username,
        context=relevant_context
    )

    data = query_messages(username)
            
    conversation = data['conversation']
    context = data['context']
    
    final_prompt = f"""
You are a helpful assistant for the company Ebogenes. 
Your role is to assist users by answering questions based on their Ebogenes genetic report. 

Guidelines: 
- Stay focused on genetics and information derived from their report. 
- Engage naturally—it's okay to greet users or acknowledge their personal comments—as long as the conversation remains centered on their Ebogenes results. 
- If users go completely off-topic, gently guide them back with a message like: 
"I'm here to help you with your Ebogenes genetic report. What would you like to explore?" 
- Always consider whether the Report Context is relevant to the genetic report before responding. 
- Provide clear, structured answers with line breaks for readability. 
- If appropriate, break your response into: 
- Overview / Summary 
-Include all relevant risks or points as bullet points
- Details or Interpretations 
- What You Can Do / Next Steps 

Stay professional, supportive, and informative.


Report Context:
{context}

Conversation:
{conversation}
"""
    #clear_terminal()
    #print(final_prompt)
    response = call_openai(final_prompt)
    assistant_response = "Assistant: " + response
    add_message(
        username=username,
        message=assistant_response,
    )
    
    return jsonify({"response": response})


def delete_report_history(username):
    file_path = get_conversation_file(username)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False