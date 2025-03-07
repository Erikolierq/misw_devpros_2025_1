import fastavro
from io import BytesIO
from pulsar.schema import Record, String, Integer, AvroSchema

class ResultCreatedSchema(Record):
    schema_version = String(default="1.0")
    result_id = Integer()
    patient = String()
    result = String()

class EventPublisher:
    def __init__(self, pulsar_client):
        self.client = pulsar_client
        try:
            self.producer = self.client.create_producer(
                "persistent://public/default/event-user",
                schema=AvroSchema(ResultCreatedSchema)
            )
        except Exception as e:
            print(f"Error creando el productor de eventos: {e}")
            raise

    def serialize_event(self, event):
        schema_version = "1.0"
        event_data = event.to_dict()
        event_data["schema_version"] = schema_version

        avro_bytes = BytesIO()
        fastavro.writer(avro_bytes, ResultCreatedSchema.schema(), [event_data])
        return avro_bytes.getvalue()

    def publish(self, event):
        try:
            serialized_event = self.serialize_event(event)
            self.producer.send(serialized_event)
            print(f"Evento publicado: {event.to_json()}")
        except Exception as e:
            print(f"Error al publicar evento: {e}")

    def close(self):
        self.client.close()
