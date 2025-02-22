import time
import os
import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:password@db_services:5432/users_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key' 

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  
    role = db.Column(db.Integer, nullable=False)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )
        return jsonify(access_token=token), 200
    return jsonify({"msg": "Credenciales inválidas"}), 401


    
def wait_for_db():
    retries = 5
    while retries:
        try:
            with app.app_context():
                db.create_all()
            print("✅ Base de datos lista")
            return
        except OperationalError:
            retries -= 1
            print("⏳ Esperando a que la base de datos esté lista...")
            time.sleep(5)
    print("❌ No se pudo conectar a la base de datos")

if __name__ == '__main__':
    wait_for_db()  
    app.run(host='0.0.0.0', port=5001)
