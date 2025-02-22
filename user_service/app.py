import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:password@db_services:5432/users_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) 
    role = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 1)  
    
    if not username or not password:
        return jsonify({"msg": "Se requieren username y password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "El username ya existe"}), 400

    new_user = User(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@app.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()  
    app.run(host='0.0.0.0', port=5004)
