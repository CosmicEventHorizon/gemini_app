import json
import os
from flask import jsonify
from retriever.search import get_relevant_chunks
from utils.model import call_openai
from utils.console import clear_terminal
from uuid import uuid4
from datetime import datetime

CONVERSATION_DIR = "data/conversations"
os.makedirs(CONVERSATION_DIR, exist_ok=True)

def get_conversation_file(username):
    return os.path.join(CONVERSATION_DIR, f"user_{username}_history.json")

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

def query_messages(username, query_text=None, n_results=10, metadata_filter=None):
    data = load_conversation(username)
    results = {
        "conversation": [],
        "context": []
    }
    
    # Reverse to get most recent messages first
    messages = conversation["messages"][::-1]
    metadatas = conversation["metadata"][::-1]
    
    # Simple filter implementation
    for msg, meta in zip(messages, metadatas):
        if metadata_filter and not all(meta["metadata"].get(k) == v for k, v in metadata_filter.items()):
            continue
            
        results["documents"].append(msg["document"])
        results["metadatas"].append(meta["metadata"])
        
        if len(results["documents"]) >= n_results:
            break
    
    return results

def handle_report_chat(prompt, report_name, username):
    try:
        relevant_context = get_relevant_chunks(prompt, report_name, 15)
        if relevant_context is None: 
            return jsonify({"response": "Please reload the database"}) 

        user_prompt = "User: " + prompt
        
        add_message(
            username=username,
            message=user_prompt,
        )
        
        conversation_history = query_messages(
            username=username,
            query_text=prompt,
            n_results=10,
            metadata_filter={"type": "conversation"}
        )
        
        context_history = query_messages(
            username=username,
            query_text=relevant_context,
            n_results=3,
            metadata_filter={"type": "conversation"}
        )
        
        conversation = '\n\n'.join([doc for doc in conversation_history['documents']])
        context = '\n'.join([meta['context'] for meta in context_history['metadatas'] if meta.get('context')])
        
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
        
        response = call_openai(final_prompt)
        
        assistant_response = "Assistant: " + response
        add_message(
            username=username,
            document=assistant_response,
            metadata={"type": "conversation", "context": ""}
        )
        
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def delete_history(username):
    """Delete conversation history for a user"""
    file_path = get_conversation_file(username)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False