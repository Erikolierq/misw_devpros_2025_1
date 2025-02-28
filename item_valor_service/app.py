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
    data = request.get_json()
    try:
        result = command_handler.handle_create_result(data.get('patient'), data.get('result'))
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400

@app.route('/results/<int:result_id>', methods=['GET'])
@jwt_required()
def get_clinical_result(result_id):
    current_user = get_jwt_identity()
    event = ResultQueriedEvent(current_user, result_id)
    event_publisher.publish(event)

    import threading
    processing_thread = threading.Thread(target=event_handler.process_pulsar_event, args=(pulsar_client,))
    processing_thread.start()
    processing_thread.join() 

    result = clinical_result_repo.get_by_id(result_id)

    if result:
        return jsonify(result.to_dict()), 200
    return jsonify({"msg": "Resultado no encontrado"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
