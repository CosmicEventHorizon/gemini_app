from flask import Flask, render_template, request
from utils.model import call_openai
from retriever.search import *
from retriever.ingest import *


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product', methods=['POST'])
def product():
    prompt = request.form['prompt']
    context = get_relevant_chunks(prompt, k=3)
    error = "Please reload the database"

    if context == None:
        return render_template('index.html', product_response=error)
    
    final_prompt = f"""
    You are a helpful assistant for the company Ebovir.
    You advertise Ebovir products and answer customer's questions.
    Answer questions based only on the context below. Do not mentioned the existence of this context to the user.
    If the question is unrelated to the company Ebovir, respond:
    'I only understand Ebovir products.'

    Context:
    {context}

    Question:
    {prompt}
    """
    
    print(final_prompt)
    response = call_openai(final_prompt)
    return render_template('index.html', product_response=response)

@app.route('/report', methods=['POST'])
def report():
    prompt = request.form['prompt']
    relevant_subsections = get_relevant_subsections(prompt,5)
    error = "Please reload the database"

    if relevant_subsections == None:
        return render_template('index.html', report_response=error)
    
    print(relevant_subsections)
    titles = relevant_subsections['documents'][0]
    page_numbers = relevant_subsections['metadatas'][0]

    relevant_subsections_text = '---Sections---\n'
    for i in range(len(titles)):
        relevant_subsections_text += f"""
{titles[i]}\n
Pages {page_numbers[i]['start_page']} to {page_numbers[i]['end_page']}
"""
        
    return render_template('index.html', report_response=relevant_subsections_text)

@app.route('/reload', methods=['POST'])
def reload():
    toc_collection()
    ingest_pdf("context/product.pdf")
    return '', 204 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
