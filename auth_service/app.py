import os
import redis
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
from infrastructure.database import db, init_db
from infrastructure.encryption_service import EncryptionService

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:password@db_services:5432/users_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key' 

db.init_app(app)
with app.app_context():
    db.create_all()
    
jwt = JWTManager(app)
redis_client = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)
limiter = Limiter(get_remote_address, app=app, default_limits=[])
encryption_service = EncryptionService()
MAX_ATTEMPTS = 5
BLOCK_TIME = 300  

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  
    role = db.Column(db.Integer, nullable=False)
    
    
@app.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    ip_address = get_remote_address()
    key = f"failed_attempts:{ip_address}"
    blocked_key = f"blocked:{ip_address}"

    if redis_client.exists(blocked_key):
        remaining_time = redis_client.ttl(blocked_key)
        return jsonify({"error": "IP bloqueada. Intenta más tarde.", "bloqueo_expira_en": remaining_time}), 403
    
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()

    if not user:
        return failed_attempt_response(ip_address, key, blocked_key)

    try:
        decrypted_password = encryption_service.decrypt(user.password)
    except Exception:
        return jsonify({"error": "Error al desencriptar la contraseña"}), 500

    if decrypted_password != password:
        return failed_attempt_response(ip_address, key, blocked_key)

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    redis_client.delete(key)
    return jsonify(access_token=token), 200


def failed_attempt_response(ip_address, key, blocked_key):
    attempts = redis_client.incr(key)
    redis_client.expire(key, BLOCK_TIME)

    if attempts >= MAX_ATTEMPTS:
        redis_client.setex(blocked_key, BLOCK_TIME, "1")
        return jsonify({"error": "Demasiados intentos fallidos. IP bloqueada por 5 minutos."}), 403

    return jsonify({"error": "Usuario o contraseña incorrectos.", "intentos_restantes": MAX_ATTEMPTS - attempts}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
