from flask import Flask, render_template, request
from utils.gemini import call_gemini
from retriever.search import get_relevant_chunks
from retriever.ingest import ingest_pdf

app = Flask(__name__)

@app.route('/')
def index():
    ingest_pdf("product.pdf")
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    prompt = request.form['prompt']
    context = get_relevant_chunks(prompt, k=3)

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
    response = call_gemini(final_prompt)
    return render_template('index.html', response=response)

if __name__ == "__main__":
    app.run(debug=True)