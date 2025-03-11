import os
import logging
import threading
import pulsar
from flask import Flask, jsonify

# Infraestructura / DB
from infrastructure.database import db, init_db
from infrastructure.repository import SagaLogRepository

# Consumidor genérico
from infrastructure.event_consumer import SagaLogConsumer

# Handler de eventos
from application.event_handler import SagaEventHandler

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# ===========================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ===========================================================================
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "postgresql://user:password@db_services:5432/saga_log_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    init_db(app)

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://pulsar:6650")
pulsar_client = pulsar.Client(PULSAR_URL)

def start_consumer_for_users():
    """
    Escucha el tópico de 'event-user'
    """
    # Envolvemos todo con app_context
    with app.app_context():
        logging.info("[SagaLog] Iniciando consumer para CREACIÓN DE USUARIOS...")
        consumer = SagaLogConsumer(
            pulsar_client=pulsar_client,
            topic="persistent://public/default/event-user",
            subscription_name="saga-log-subscription-users",
            event_handler=SagaEventHandler
        )
        consumer.listen()

def start_consumer_for_results():
    """
    Escucha el tópico de 'event-topic'
    """
    with app.app_context():
        logging.info("[SagaLog] Iniciando consumer para CREACIÓN DE RESULTADOS...")
        consumer = SagaLogConsumer(
            pulsar_client=pulsar_client,
            topic="persistent://public/default/event-topic",
            subscription_name="saga-log-subscription-results",
            event_handler=SagaEventHandler
        )
        consumer.listen()

thread_users = threading.Thread(target=start_consumer_for_users, daemon=True)
thread_results = threading.Thread(target=start_consumer_for_results, daemon=True)

thread_users.start()
thread_results.start()

@app.route("/saga/logs", methods=["GET"])
def get_saga_logs():
    """
    Devuelve todos los logs guardados en la tabla saga_log
    """
    logs = SagaLogRepository.get_all_logs()
    return jsonify([log.to_dict() for log in logs]), 200

@app.route("/health", methods=["GET"])
def health_check():
    logging.info("[SagaLog] Se recibió /health")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    logging.info("[SagaLog] 🚀 Iniciando servicio en puerto 5007")
    app.run(host="0.0.0.0", port=5007, debug=False)
