from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

MICROSERVICES = {
    "auth": "http://auth_service:5001",
    "certificator": "http://certificator_service:5002",
    "item_valor": "http://item_valor_service:5003",
    "users": "http://users_service:5004",
}

@app.route('/')
def home():
    return jsonify({"message": "BFF Running"})

@app.route('/login', methods=["POST"])
def login():
    auth_data = request.json
    response = requests.post(f"{MICROSERVICES['auth']}/login", json=auth_data)
    # Aca se obtiene un access_token
    return jsonify(response.json()), response.status_code

@app.route('/user-profile', methods=["GET"])
def user_profile():
    user_id = request.headers.get("User-Id")
    if not user_id:
        return jsonify({"error": "User-Id header is required"}), 400
    
    user_data = requests.get(f"{MICROSERVICES['users']}/users/{user_id}").json()
    certs = requests.get(f"{MICROSERVICES['certificator']}/certificates/{user_id}").json()
    
    return jsonify({
        "user": user_data,
        "certifications": certs
    })

@app.route('/dashboard', methods=["GET"])
def dashboard():
    user_id = request.headers.get("User-Id")
    if not user_id:
        return jsonify({"error": "User-Id header is required"}), 400
    
    user_info = requests.get(f"{MICROSERVICES['users']}/users/{user_id}").json()
    user_items = requests.get(f"{MICROSERVICES['item_valor']}/items/{user_id}").json()
    
    return jsonify({
        "user": user_info,
        "items": user_items
    })

@app.route('/users', methods=["POST"])
def create_user():
    user_data = request.json
    response = requests.post(f"{MICROSERVICES['users']}/users", json=user_data)
    return jsonify(response.json()), response.status_code

@app.route('/users', methods=["GET"])
def get_all_users():
    response = requests.get(f"{MICROSERVICES['users']}/users")
    return jsonify(response.json()), response.status_code

@app.route('/results', methods=["POST"])
def create_item_valor():
    item_data = request.json
    response = requests.post(
        f"{MICROSERVICES['item_valor']}/results", 
        json=item_data,
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return jsonify(response.json()), response.status_code

@app.route('/results/<user_id>', methods=["GET"])
def get_item_valor(user_id):
    response = requests.get(
        f"{MICROSERVICES['item_valor']}/results/{user_id}",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
