from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  
jwt = JWTManager(app)

@app.route('/validate', methods=['GET'])
@jwt_required()
def validate():
    claims = get_jwt()  
    role = claims.get('role') 

    if role == 1:
        return jsonify({'allowed': False, 'message': 'Acceso denegado para rol 1'}), 403
    elif role == 2:
        return jsonify({'allowed': True, 'message': 'Acceso permitido para rol 2'}), 200
    return jsonify({'allowed': False, 'message': 'Rol desconocido'}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
