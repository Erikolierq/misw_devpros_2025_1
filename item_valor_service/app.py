import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import requests

from infrastructure.database import db, init_db
from infrastructure.repository import ClinicalResultRepository
from infrastructure.event_publisher import EventPublisher
from application.result_query_service import ResultQueryService
from domain.clinical_result import ClinicalResult

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql://user:password@db:5432/users_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

db.init_app(app)
with app.app_context():
    db.create_all()  

jwt = JWTManager(app)

clinical_result_repo = ClinicalResultRepository(db.session)
event_publisher = EventPublisher()

result_query_service = ResultQueryService(clinical_result_repo, event_publisher)

@app.route('/results', methods=['POST'])
@jwt_required()
def create_clinical_result():
    data = request.get_json()
    patient = data.get('patient')
    result_text = data.get('result')
    
    if not patient or not result_text:
        return jsonify({"msg": "Faltan campos requeridos: 'patient' y 'result'"}), 400
    
    new_result = ClinicalResult(patient=patient, result=result_text)
    
    clinical_result_repo.add(new_result)
    
    from domain.events import ResultCreatedEvent
    event = ResultCreatedEvent(new_result.id, patient, result_text)
    event_publisher.publish(event)
    
    return jsonify(new_result.to_dict()), 201

@app.route('/results/<int:result_id>', methods=['GET'])
@jwt_required()
def get_clinical_result(result_id):
    current_user = get_jwt_identity()
    
    token = request.headers.get('Authorization')
    headers = {"Authorization": token}
    cert_response = requests.get("http://certificator_service:5002/validate", headers=headers)
    if cert_response.status_code != 200:
        return jsonify({"msg": "No autorizado para acceder a este recurso"}), 403

    from domain.events import ResultQueriedEvent
    event = ResultQueriedEvent(current_user, result_id)

    event_publisher.publish(event)
    
    result = clinical_result_repo.get_by_id(result_id)
    if result:
        return jsonify(result.to_dict()), 200
    return jsonify({"msg": "Resultado no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
