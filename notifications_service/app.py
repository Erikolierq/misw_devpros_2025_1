# notifications_service/app.py
import os
import threading
import logging
import pulsar
from flask import Flask, jsonify

from infrastructure.event_consumer import EventConsumer
from application.notification_handler import NotificationHandler

# ===============================
# CONFIGURACIÓN DEL LOGGING
# ===============================
# Establecer el nivel de logging a INFO para ver mensajes informativos y de error
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# ===============================
# CONFIGURACIÓN DE PULSAR
# ===============================
PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://pulsar:6650")
pulsar_client = pulsar.Client(PULSAR_URL)

# ===============================
# INSTANCIAR HANDLER
# ===============================
notification_handler = NotificationHandler()

def start_consumer():
    logging.info("[Notifications] Iniciando consumidor en un hilo aparte...")
    consumer = EventConsumer(
        pulsar_client=pulsar_client,
        subscription_name="notifications-subscription",
        topic="persistent://public/default/event-user",
        notification_handler=notification_handler
    )
    consumer.listen()

# ===============================
# LANZAR CONSUMIDOR EN UN HILO
# ===============================
consumer_thread = threading.Thread(target=start_consumer, daemon=True)
consumer_thread.start()

@app.route("/health", methods=["GET"])
def health_check():
    logging.info("[Notifications] Se recibió solicitud de /health")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    logging.info("[Notifications] Arrancando app Flask en puerto 5006")
    app.run(host="0.0.0.0", port=5006, debug=False)
