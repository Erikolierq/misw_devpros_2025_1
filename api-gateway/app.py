from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

MICROSERVICES = {
    "auth": "http://auth_service:5001",
    "certificator": "http://certificator_service:5002",
    "item_valor": "http://item_valor_service:5003",
    "users": "http://users_service:5004",
}

@app.route('/')
def home():
    return jsonify({"message": "API Gateway Running"})

@app.route('/auth/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
def proxy_auth(path):
    return proxy_request("auth", path)

@app.route('/certificator/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
def proxy_certificator(path):
    return proxy_request("certificator", path)

@app.route('/item_valor/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
def proxy_item_valor(path):
    return proxy_request("item_valor", path)

@app.route('/users/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
def proxy_users(path):
    return proxy_request("users", path)

def proxy_request(service, path):
    url = f"{MICROSERVICES[service]}/{path}"
    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            json=request.get_json() if request.data else None
        )
        try:
            return jsonify(response.json()), response.status_code
        except requests.exceptions.JSONDecodeError:
            return jsonify({"error": "Invalid JSON response from service", "service": service, "status_code": response.status_code, "response_text": response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Service request failed", "service": service, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
