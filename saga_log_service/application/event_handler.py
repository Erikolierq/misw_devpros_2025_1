import logging
import json
from infrastructure.repository import SagaLogRepository

class SagaEventHandler:
    @staticmethod
    def process_event(topic, message):
        """
        Procesa eventos recibidos desde Apache Pulsar y los almacena en la BD.
        """
        try:
            payload_str = message.data().decode("utf-8").strip()
            logging.info(f"[SagaEventHandler] 📩 Evento recibido de {topic}: {payload_str}")

            # Ignorar mensajes de inicialización ("INIT-TOPIC")
            if payload_str == "INIT-TOPIC":
                logging.warning("[SagaEventHandler]  Mensaje de inicialización detectado, ignorando.")
                return

            # Parsear el mensaje como JSON
            try:
                event_data = json.loads(payload_str)
            except json.JSONDecodeError as e:
                logging.error(f"[SagaEventHandler]  Error al parsear JSON: {str(e)}")
                return  # Ignora el mensaje si no es JSON válido

            # Determinar el tipo de evento (UserCreated, ResultCreated, etc.)
            event_type = event_data.get("event_type", "UNKNOWN")

            # En caso quieras lógica específica:
            if topic == "persistent://public/default/event-user":
                SagaEventHandler.handle_user_created(event_data)
            elif topic == "persistent://public/default/event-topic":
                SagaEventHandler.handle_result_created(event_data)
            else:
                logging.warning(f"[SagaEventHandler]  Tópico desconocido: {topic}")

            # Guardar en la BD
            SagaLogRepository.save_log(
                topic=topic,
                event_type=event_type,
                status="PROCESSED",
                data=event_data
            )
            logging.info(f"[SagaEventHandler]  Evento almacenado en BD: {event_data}")

        except Exception as e:
            logging.error(f"[SagaEventHandler]  Error procesando evento: {str(e)}")

    @staticmethod
    def handle_user_created(event_data):
        user_id = event_data.get("id")
        username = event_data.get("username")
        role = event_data.get("role")
        logging.info(f"[SagaEventHandler]  Procesando USER -> user_id={user_id}, username={username}, role={role}")

    @staticmethod
    def handle_result_created(event_data):
        result_id = event_data.get("id")
        patient = event_data.get("patient")
        result_value = event_data.get("result")
        logging.info(f"[SagaEventHandler]  Procesando RESULT -> ID={result_id}, Paciente={patient}, Resultado={result_value}")
