from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

MICROSERVICES = {
    "auth": "http://auth_service:5001",
    "certificator": "http://certificator_service:5002",
    "item_valor": "http://item_valor_service:5003",
    "users": "http://users_service:5004",
    "notifications": "http://notifications_service:5006",
    "saga_log": "http://saga_log_service:5007"
}

def forward_request(method, service, endpoint, data=None, headers=None):
    url = f"{MICROSERVICES[service]}{endpoint}"
    response = requests.request(method, url, json=data, headers=headers)
    return response.json(), response.status_code

@app.route('/')
def home():
    return jsonify({"message": "BFF Running"})

@app.route('/login', methods=["POST"])
def login():
    auth_data = request.json
    return forward_request("POST", "auth", "/login", data=auth_data)

@app.route('/user-profile', methods=["GET"])
def user_profile():
    user_id = request.headers.get("user_id")
    if not user_id:
        return jsonify({"error": "User-Id header is required"}), 400
    
    user_data, _ = forward_request("GET", "users", f"/users/{user_id}")
    certs, _ = forward_request("GET", "certificator", f"/certificates/{user_id}")
    
    return jsonify({"user": user_data, "certifications": certs})

@app.route('/dashboard', methods=["GET"])
def dashboard():
    user_id = request.headers.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id header is required"}), 400
    
    user_info, _ = forward_request("GET", "users", f"/users/{user_id}")
    user_items, _ = forward_request("GET", "item_valor", f"/items/{user_id}")
    
    return jsonify({"user": user_info, "items": user_items})

@app.route('/users', methods=["POST"])
def create_user():
    return forward_request("POST", "users", "/users", data=request.json)

@app.route('/users', methods=["GET"])
def get_all_users():
    return forward_request("GET", "users", "/users")

@app.route('/results', methods=["POST"])
def create_item_valor():
    headers = {"Authorization": request.headers.get("Authorization")}
    return forward_request("POST", "item_valor", "/results", data=request.json, headers=headers)

@app.route('/results/<user_id>', methods=["GET"])
def get_item_valor(user_id):
    headers = {"Authorization": request.headers.get("Authorization")}
    return forward_request("GET", "item_valor", f"/results/{user_id}", headers=headers)
@app.route('/notifications/health', methods=["GET"])
def notifications_health():
    """
    Endpoint para verificar la salud del notifications_service desde el API Gateway.
    """
    return forward_request("GET", "notifications", "/health")

@app.route('/saga/logs', methods=["GET"])
def get_saga_logs():
    return forward_request("GET", "saga_log", "/saga/logs")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
