# notifications_service/app.py
import os
import threading
import logging
import pulsar
from flask import Flask, jsonify

from infrastructure.event_consumer import EventConsumer
from application.notification_handler import NotificationHandler

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://pulsar:6650")
pulsar_client = pulsar.Client(PULSAR_URL)

notification_handler = NotificationHandler()

def start_consumer_for_users():
    """
    Escucha el tópico donde se publican eventos de creación de usuarios
    """
    logging.info("[Notifications] Iniciando consumer para creación de usuarios...")
    consumer = EventConsumer(
        pulsar_client=pulsar_client,
        subscription_name="notifications-subscription-users",
        topic="persistent://public/default/event-user",  # <-- Tópico de usuarios
        notification_handler=notification_handler,
        event_type="UserCreated"  # Parámetro opcional para distinguir
    )
    consumer.listen()

def start_consumer_for_results():
    """
    Escucha el tópico donde se publican eventos de creación de resultados
    """
    logging.info("[Notifications] Iniciando consumer para creación de resultados...")
    consumer = EventConsumer(
        pulsar_client=pulsar_client,
        subscription_name="notifications-subscription-results",
        topic="persistent://public/default/event-topic",  # <-- Tópico de resultados
        notification_handler=notification_handler,
        event_type="ResultCreated" # Parámetro opcional para distinguir
    )
    consumer.listen()


# Lanzamos ambos consumidores en hilos separados
thread_users = threading.Thread(target=start_consumer_for_users, daemon=True)
thread_results = threading.Thread(target=start_consumer_for_results, daemon=True)

thread_users.start()
thread_results.start()

@app.route("/health", methods=["GET"])
def health_check():
    logging.info("[Notifications] Se recibió solicitud de /health")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    logging.info("[Notifications] Arrancando app Flask en puerto 5006")
    app.run(host="0.0.0.0", port=5006, debug=False)
