import logging
import fastavro
from io import BytesIO
from pulsar.schema import Record, String, Integer, AvroSchema

class ResultCreatedSchema(Record):
    schema_version = String(default="1.0")
    id = Integer()
    username = String()
    password = String()
    role = Integer()

class EventPublisher:
    def __init__(self, pulsar_client):
        self.client = pulsar_client
        try:
            self.producer = self.client.create_producer(
                "persistent://public/default/event-user",
                schema=AvroSchema(ResultCreatedSchema)
            )
            logging.info("[EventPublisher] Productor creado para persistent://public/default/event-user")
            print("[EventPublisher] Productor creado correctamente")
        except Exception as e:
            logging.error(f"[EventPublisher] Error creando el productor de eventos: {e}")
            print(f"Error creando el productor de eventos: {e}")
            raise

    def serialize_event(self, event):
        """
        Serializa el evento usando fastavro y la clase ResultCreatedSchema.
        """
        schema_version = "1.0"
        event_data = event.to_dict()
        event_data["schema_version"] = schema_version

        avro_bytes = BytesIO()
        fastavro.writer(avro_bytes, ResultCreatedSchema.schema(), [event_data])
        
        # Log adicional si quieres ver los datos que se van a serializar:
        logging.debug(f"[EventPublisher] Serializando evento: {event_data}")

        return avro_bytes.getvalue()

    def publish(self, event):
        """
        Publica el evento en el tópico usando AvroSchema.
        """
        try:
            serialized_event = self.serialize_event(event)
            self.producer.send(serialized_event)

            logging.info(f"[EventPublisher] Evento publicado: {event.to_json()}")
            print(f"Evento publicado: {event.to_json()}")
        except Exception as e:
            logging.error(f"[EventPublisher] Error al publicar evento: {e}")
            print(f"Error al publicar evento: {e}")

    def close(self):
        """
        Cierra el cliente de Pulsar.
        """
        logging.info("[EventPublisher] Cerrando el cliente de Pulsar.")
        print("[EventPublisher] Cerrando el cliente de Pulsar.")
        self.client.close()
