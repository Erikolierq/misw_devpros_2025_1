import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pulsar
from infrastructure.database import db, init_db
from domain.events import ResultQueriedEvent
from infrastructure.database import db, init_db
from infrastructure.repository import UserRepository
from infrastructure.event_publisher import EventPublisher
from application.command_handlers import CommandHandler
from application.event_handlers import EventHandler
from infrastructure.event_store import EventStoreRepository
from infrastructure.event_consumer import EventConsumer
import threading
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:password@db_services:5432/users_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()
    
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per minute"]
)


pulsar_client = pulsar.Client("pulsar://pulsar:6650")
user_repo = UserRepository(db.session)
event_store_repo = EventStoreRepository(db.session)
event_publisher = EventPublisher(pulsar_client)

command_handler = CommandHandler(user_repo, event_publisher, event_store_repo)
event_handler = EventHandler(user_repo, event_store_repo)

@app.route('/users', methods=['POST'])
@limiter.limit("50 per minute") 
def create_user():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"msg": "No se enviaron datos"}), 400

        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 1)  

        if not username or not password:
            return jsonify({"msg": "Se requieren username y password"}), 400

        existing_user = user_repo.get_by_username(username)
        if existing_user:
            return jsonify({"msg": "El usuario ya está registrado"}), 409

        result_data = command_handler.handle_create_result(username, password, role)
        return jsonify(result_data), 201
    
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error en create_user: {str(e)}")
        return jsonify({"msg": "Error interno del servidor"}), 500

@app.route('/users', methods=['GET'])
@limiter.limit("50 per minute") 
def list_users():
    users = user_repo.get_all_users()

    if not users:
        return jsonify({"msg": "No hay usuarios registrados"}), 200

    event = ResultQueriedEvent(1, users)
    event_publisher.publish(event)

    return jsonify(users), 200

def start_consumer():
    consumer = EventConsumer("pulsar://pulsar:6650")
    consumer.listen()

consumer_thread = threading.Thread(target=start_consumer, daemon=True)
consumer_thread.start()

if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()  
    app.run(host='0.0.0.0', port=5004)