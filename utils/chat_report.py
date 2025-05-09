from flask import jsonify
from retriever.search import get_relevant_chunks
from utils.model import call_openai
from utils.console import clear_terminal
import chromadb
from uuid import uuid4

chroma_client = chromadb.PersistentClient(path="data/chroma_db")

def handle_report_chat(prompt, report_name, username):
    try:
        collection = chroma_client.get_collection(name=f"user_{username}_history")
    except:
        collection = chroma_client.create_collection(name=f"user_{username}_history")
    
    relevant_context = get_relevant_chunks(prompt, report_name, 15)
    if relevant_context is None: 
        return jsonify({"response": "Please reload the database"}) 

    user_prompt = "User: " + prompt
    collection.add(
        documents=[user_prompt],
        metadatas=[{"type": "conversation", "context": relevant_context}],
        ids=[str(uuid4())]
    )
    
    conversation_history = collection.query(
        query_texts=[prompt],
        n_results=10,
        where={"type": "conversation"}
    )
    
    context_history = collection.query(
        query_texts=[relevant_context],
        n_results=3,
        where={"type": "conversation"}
    )
    
    conversation = '\n\n'.join([doc for doc in conversation_history['documents'][0]])
    context = '\n'.join([meta['context'] for meta in context_history['metadatas'][0]])
    
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
    
    clear_terminal()
    print(final_prompt)
    response = call_openai(final_prompt)
    
    assistant_response = "Assistant: " + response
    collection.add(
        documents=[assistant_response],
        metadatas=[{"type": "conversation", "context": ""}],
        ids=[str(uuid4())]
    )
    
    return jsonify({"response": response})


def delete_history(username):
  history_name = f"user_{username}_history"
  if history_name in [c.name for c in chroma_client.list_collections()]:
    chroma_client.delete_collection(history_name)

  