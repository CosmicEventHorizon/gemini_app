import json
import os
from flask import jsonify
from retriever.search import get_relevant_chunks
from utils.model import call_openai
from utils.console import clear_terminal

CONVERSATION_DIR = "data/conversations"
os.makedirs(CONVERSATION_DIR, exist_ok=True)

def get_conversation_file(guest_id):
    return os.path.join(CONVERSATION_DIR, f"user_{guest_id}_product_history.json")

def load_conversation(guest_id):
    file_path = get_conversation_file(guest_id)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {"conversation": [], "context": []}

def save_conversation(guest_id, data):
    file_path = get_conversation_file(guest_id)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def add_message(guest_id, message):
    data = load_conversation(guest_id)
    print(data)
    data["conversation"].append({
        "message": message,
    })
    save_conversation(guest_id, data)

def add_context(guest_id, context):
    data = load_conversation(guest_id)
    data["context"].append({
        "context": context,
    })
    save_conversation(guest_id, data)

def query_messages(guest_id):
    data = load_conversation(guest_id)
    result = {
        "conversation": [],
        "context": []
    }
    result['conversation'] = '\n\n'.join(m['message'] for m in data['conversation'][-10:])
    result['context'] = '\n'.join(c['context'] for c in data['context'][-3:])
    return result

def handle_product_chat(prompt, guest_id):
    relevant_context = get_relevant_chunks(prompt, "product", 15)
    if relevant_context is None: 
        return jsonify({"response": "Please reload the database"}) 

    user_prompt = "User: " + prompt
    
    add_message(
        guest_id=guest_id,
        message=user_prompt,
    )

    add_context(
        guest_id=guest_id,
        context=relevant_context
    )

    data = query_messages(guest_id)
            
    conversation = data['conversation']
    context = data['context']
    
    final_prompt = f"""
You are a helpful assistant for the company Ebogenes.
Your role is to assist users by answering questions based on the Ebogenes products.

Guidelines:
Stay focused on the product information and content derived directly from the product context.
Engage naturally—it's okay to greet users or acknowledge their personal comments—as long as the conversation remains centered on the Ebogenes product information.
If users go completely off-topic, gently guide them back with a message like:
"I'm here to help you with Ebogenes products. What would you like to explore?"
Always consider whether the user’s question relates to the product context before responding.
Provide clear, structured answers with line breaks for readability.

If appropriate, break your response into:
Overview / Summary
Include all key product features or points as bullet points
Stay professional, supportive, and informative


Product Context:
{context}

Conversation:
{conversation}
"""

    #clear_terminal()
    #print(final_prompt)
    response = call_openai(final_prompt)
    assistant_response = "Assistant: " + response
    add_message(
        guest_id=guest_id,
        message=assistant_response,
    )
    
    return jsonify({"response": response})


def delete_product_history(guest_id):
    file_path = get_conversation_file(guest_id)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False