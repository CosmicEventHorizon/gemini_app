from flask import Flask, session, render_template, request, jsonify
from utils.model import call_openai
from flask_session import Session
from retriever.search import *
from retriever.ingest import *
import os


app = Flask(__name__)
app.secret_key = os.urandom(24) 

app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = './flask_session/' 

Session(app)


@app.route('/')
def index():
    user_id = 123456789
    if 'user_id' not in session:
        session['user_id'] = user_id
    session.modified = True
    return render_template('home.html')

@app.route('/genereportbot')
def genereportbot():
    user_id = session.get('user_id', None)
    report_name = get_report_db_name(user_id)
    relevant_context = get_relevant_chunks("test",report_name,2)
    if relevant_context == None:
        reload()
    return render_template('report_bot.html')

@app.route('/productbot')
def productbot():
    context = get_relevant_chunks("test", "product_collection", 2)
    if context == None:
        reload()
    return render_template('product_bot.html')

@app.route('/product', methods=['POST'])
def product():
    data = request.get_json()
    prompt = data.get('prompt')
    relevant_context = get_relevant_chunks(prompt,"product_collection",5)
    if relevant_context == None: 
        return jsonify({"response":"Please reload the database"}) 
    
    if 'conversation' not in session or 'context' not in session:
        session['conversation_product'] = []
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

@app.route('/report', methods=['POST'])
def report():
    data = request.get_json()
    prompt = data.get('prompt')
    user_id = session.get('user_id', None)
    if user_id == None:
        return jsonify({"response":"User ID not found"}) 
    report_name = get_report_db_name(user_id)
    relevant_context = get_relevant_chunks(prompt,report_name,15)
    if relevant_context == None: 
        return jsonify({"response":"Please reload the database"}) 

    if 'conversation' not in session or 'context' not in session:
        session['conversation'] = []
        session['context'] = []
    
    user_prompt = "User: " + prompt

    session['conversation'].append(user_prompt)
    session['context'].append(relevant_context)
    conversation = '\n\n'.join(session['conversation'][-10:])
    context = '\n'.join(session['context'][-3:])
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
    session['conversation'].append(assistant_response)
    session.modified = True
    return jsonify({"response": response})

@app.route('/reload', methods=['POST'])
def reload():
    user_id = session.get('user_id', None)
    if user_id is None:
        return '',404
    report_name = get_report_db_name(user_id)
    ingest_pdf("context/report.pdf", report_name)
    ingest_pdf("context/product.pdf", "product_collection")
    return '', 204 

@app.route('/generate_user', methods=['POST'])
def generate_user():
    user_id = 123456789
    if 'user_id' not in session:
        session['user_id'] = user_id
    session.modified = True
    return '', 204 

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
