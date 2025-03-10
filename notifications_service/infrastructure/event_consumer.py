# notifications_service/infrastructure/event_consumer.py
import pulsar
import json
import logging
from application.notification_handler import NotificationHandler

class EventConsumer:
    def __init__(self, pulsar_client, subscription_name: str, topic: str, notification_handler: NotificationHandler):
        self.client = pulsar_client
        self.subscription_name = subscription_name
        self.topic = topic
        self.notification_handler = notification_handler

        logging.info(f"[EventConsumer] Suscribiéndose a: {self.topic} con la suscripción: {self.subscription_name}")
        print(f"Creando consumer para topic={self.topic}, subs={self.subscription_name}")

        self.consumer = self.client.subscribe(
            topic=self.topic,
            subscription_name=self.subscription_name,
            consumer_type=pulsar.ConsumerType.Shared
        )

    def listen(self):
        logging.info(f"[EventConsumer] Escuchando mensajes en {self.topic}...")
        while True:
            try:
                msg = self.consumer.receive(timeout_millis=5000)
                if msg:
                    payload_str = msg.data().decode("utf-8").strip()
                    logging.info(f"[EventConsumer] Mensaje recibido (raw): {payload_str}")
                    print(f"Mensaje crudo: {payload_str}")

                    # Validar que parezca JSON
                    if not payload_str.startswith("{") or not payload_str.endswith("}"):
                        logging.warning(f"[EventConsumer] Ignorando mensaje no válido: {payload_str}")
                        self.consumer.acknowledge(msg)
                        continue

                    try:
                        event_data = json.loads(payload_str)
                        logging.info(f"[EventConsumer] Mensaje decodificado: {event_data}")
                        print(f"Mensaje decodificado: {event_data}")

                        # Invocar el NotificationHandler
                        self.notification_handler.handle_user_created(event_data)

                        # Acknowledge del mensaje
                        self.consumer.acknowledge(msg)
                        logging.info("[EventConsumer] Mensaje ACKed con éxito")

                    except json.JSONDecodeError as e:
                        logging.error(f"[EventConsumer] Error al parsear JSON ({str(e)}): {payload_str}")
                        print(f"ERROR parseando JSON: {payload_str}")
                        self.consumer.acknowledge(msg)

            except pulsar.Timeout:
                # No hay mensajes nuevos
                pass
            except Exception as e:
                logging.error(f"[EventConsumer] Error procesando mensaje: {str(e)}")
                print(f"ERROR general: {str(e)}")
                self.consumer.negative_acknowledge(msg)

    def close(self):
        logging.info("[EventConsumer] Cerrando cliente de Pulsar...")
        self.client.close()
