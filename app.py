from flask import Flask, render_template, request
import google.generativeai as genai
import os

app = Flask(__name__)

api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)  
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    prompt = request.form['prompt']
    response = model.generate_content(prompt).text
    return render_template('index.html', response=response)
