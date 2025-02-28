import os
import json
import threading
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pulsar import Client, ConsumerType
from pulsar.schema import JsonSchema
from domain.schemas import UserCommandSchema
from application.command_handler import CommandHandler
from application.event_handler import EventHandler

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'postgresql://user:password@db_services:5432/users_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configuración de Apache Pulsar
PULSAR_URL = os.getenv('PULSAR_URL', 'pulsar://pulsar:6650')
client = Client(PULSAR_URL)

# Productor para eventos de usuario con JsonSchema
event_producer = client.create_producer('user_events', schema=JsonSchema(UserCommandSchema))

# Consumidor para comandos de usuario
command_consumer = client.subscribe(
    'user_commands',
    subscription_name='user_service_sub',
    consumer_type=ConsumerType.Shared
)

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
    """ Recibe una solicitud HTTP y envía un comando a Pulsar """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 1)

    if not username or not password:
        return jsonify({"msg": "Se requieren username y password"}), 400

    command = {
        "type": "CreateUser",
        "version": 1,
        "data": {
            "username": username,
            "password": password,
            "role": role
        }
    }

    event_producer.send(command)
    
    return jsonify({"msg": "Comando enviado"}), 202

@app.route('/users', methods=['GET'])
def list_users():
    """ Devuelve la lista de usuarios almacenados en la BD """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

def process_commands():
    """ Procesa los comandos recibidos en Pulsar y guarda en la BD """
    while True:
        msg = command_consumer.receive()
        try:
            command_data = json.loads(msg.data())

            if command_data["type"] == "CreateUser":
                new_user = User(
                    username=command_data["data"]["username"],
                    password=command_data["data"]["password"],
                    role=command_data["data"]["role"]
                )
                db.session.add(new_user)
                db.session.commit()

                # Emitir evento de usuario creado
                event = {
                    "type": "UserCreated",
                    "version": 1,
                    "data": {
                        "user_id": new_user.id,
                        "username": new_user.username,
                        "role": new_user.role
                    }
                }
                event_producer.send(event)

            command_consumer.acknowledge(msg)

        except Exception as e:
            print(f"Error procesando mensaje: {e}")
            command_consumer.negative_acknowledge(msg)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Iniciar el consumidor de comandos
    command_handler = CommandHandler(PULSAR_URL)
    threading.Thread(target=command_handler.listen, daemon=True).start()

    # Iniciar el manejador de eventos
    event_handler = EventHandler(PULSAR_URL, app.config['SQLALCHEMY_DATABASE_URI'])
    threading.Thread(target=event_handler.listen, daemon=True).start()

    # Ejecutar el procesamiento de comandos en el hilo principal
    process_commands()
