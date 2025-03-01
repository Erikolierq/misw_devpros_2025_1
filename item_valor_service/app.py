import os
import pulsar
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from domain.events import ResultQueriedEvent
from infrastructure.database import db, init_db
from infrastructure.repository import ClinicalResultRepository
from infrastructure.event_publisher import EventPublisher
from application.command_handlers import CommandHandler
from application.event_handlers import EventHandler
from infrastructure.event_store import EventStoreRepository
from infrastructure.event_consumer import EventConsumer
import threading

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
pulsar_client = pulsar.Client("pulsar://pulsar:6650")
clinical_result_repo = ClinicalResultRepository(db.session)
event_store_repo = EventStoreRepository(db.session)
event_publisher = EventPublisher(pulsar_client)

command_handler = CommandHandler(clinical_result_repo, event_publisher, event_store_repo)
event_handler = EventHandler(clinical_result_repo, event_store_repo)

@app.route('/results', methods=['POST'])
@jwt_required()
def create_clinical_result():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"msg": "No se enviaron datos"}), 400

        patient = data.get('patient')
        result = data.get('result')

        if not patient or not result:
            return jsonify({"msg": "Faltan campos requeridos: 'patient' y 'result'"}), 400

        result_data = command_handler.handle_create_result(patient, result)
        
        return jsonify(result_data), 201

    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error en create_clinical_result: {str(e)}")
        return jsonify({"msg": "Error interno del servidor"}), 500


@app.route('/results/<int:result_id>', methods=['GET'])
@jwt_required()
def get_clinical_result(result_id):
    current_user = get_jwt_identity()
    
    result = clinical_result_repo.get_by_id(result_id)

    if not result:
        return jsonify({"msg": "Resultado no encontrado"}), 404
    event = ResultQueriedEvent(current_user, result_id)
    event_publisher.publish(event)

    return jsonify(result.to_dict()), 200

def start_consumer():
    consumer = EventConsumer("pulsar://pulsar:6650")
    consumer.listen()

# Iniciar consumidor en un hilo separado
consumer_thread = threading.Thread(target=start_consumer, daemon=True)
consumer_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
