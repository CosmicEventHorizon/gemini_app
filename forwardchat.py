from flask import Flask, render_template, request, make_response, jsonify, redirect, url_for
from utils.auth import hash_password, check_password, add_user, get_user, generate_jwt, get_authorization_info
from retriever.ingest import ingest_pdf, check_user_report, get_sql_entry, get_chromadb_reports
from utils.chat_report import handle_report_chat, delete_report_history
from utils.chat_product import handle_product_chat, delete_product_history
import uuid
import os


app = Flask(__name__)


@app.route('/')
def home():
    new_guest_id = str(uuid.uuid4())
    resp = make_response()
    resp.set_cookie('guest_id', new_guest_id)
    print("New guest ID set!")
    token = request.cookies.get('jwt_token')
    if token is None or get_authorization_info(token)[0] is False:
        resp.headers['Location'] = url_for('login')
        resp.status_code = 302 #redirect code
        return resp
    user = get_authorization_info(token)
    username = user[1]
    delete_report_history(username)
    resp.set_data(render_template('dashboard.html', userName=username))
    return resp

@app.route('/signup', methods=['GET','POST'])
def signup_post():
    if request.method == 'GET':
            return render_template('signup.html')
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    dob = request.form['dob']
    
    if get_user(username):
        return jsonify({'message': 'User already exists'}), 409
    
    hashed_password = hash_password(password)
    add_user(username, hashed_password, email, first_name, last_name, dob)
    return jsonify({'message': 'User registered successfully'}), 201
     
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    user = get_user(username)
    if not user or not check_password(user[2], password): 
        return jsonify({'message': 'Invalid username or password'}), 401
    token = generate_jwt(username)
    response = make_response(jsonify({'message': 'Successfully logged in'}), 202)
    response.set_cookie('jwt_token', token, httponly=True)
    return response

@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({'message': 'Successfully logged out'}), 202)
    response.set_cookie('jwt_token', '', expires=0, httponly=True)
    return response

@app.route('/add-report', methods=['POST'])
def addReport():
    token = request.cookies.get('jwt_token')
    report_name = request.form['report_name']
    user = get_authorization_info(token)
    username = user[1]
    report_name_exists = check_user_report(report_name)
    if report_name_exists is True:
            return jsonify({'message':'Report already associated with a user!'}), 409
    response = ingest_pdf(username, report_name)
    if response == False:
        return jsonify({'message':'Report does not exist!'}), 404
    else:
        return jsonify({'message':'Report submitted! Please wait a few minutes before it shows under your reports.'}), 202


@app.route('/product', methods=['GET','POST'])
def product():
    if request.method == 'GET':
            return render_template('product_bot.html')
    data = request.get_json()
    prompt = data.get('prompt')
    guest_id = request.cookies.get('guest_id')
    return handle_product_chat(prompt,guest_id)


@app.route('/report', methods=['GET','POST'])
def report():
    if request.method == 'GET':
            return render_template('report_bot.html')
    token = request.cookies.get('jwt_token')
    user = get_authorization_info(token)
    username = user[1]
    data = request.get_json()
    prompt = data.get('prompt')
    report_name = data.get('report')
    if report_name not in get_report_names(username):
        return '', 403
    return handle_report_chat(prompt,report_name,username)

#polling endpoint
@app.route('/reload/status')
def reload_status():
    token = request.cookies.get('jwt_token')
    user = get_authorization_info(token)
    username = user[1]
    report_names = get_report_names(username)
    if report_names is None:
        return jsonify({"reports": []}) 
    reports = get_chromadb_reports(report_names)
    return jsonify({
        "reports": reports,
    }), 200

def get_report_names(username):
    report_tuples = get_sql_entry(username)
    if not report_tuples:
        return None
    report_names= [report[2] for report in report_tuples]
    return report_names

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
