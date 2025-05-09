from flask import session, jsonify
from retriever.search import get_relevant_chunks
from utils.openai_utils import call_openai  
from utils.console import clear_terminal  

def handle_product_chat(prompt):
    relevant_context = get_relevant_chunks(prompt, "product_collection", 5)
    if relevant_context is None:
        return jsonify({"response": "Please reload the database"})

    if 'conversation_product' not in session:
        session['conversation_product'] = []
    if 'context_product' not in session:
        session['context_product'] = []

    user_prompt = "User: " + prompt
    session['conversation_product'].append(user_prompt)
    session['context_product'].append(relevant_context)

    conversation = '\n\n'.join(session['conversation_product'][-10:])
    context = '\n'.join(session['context_product'][-3:])

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

    clear_terminal()
    print(final_prompt)
    response = call_openai(final_prompt)
    assistant_response = "Assistant: " + response
    session['conversation_product'].append(assistant_response)
    session.modified = True

    return jsonify({"response": response})
