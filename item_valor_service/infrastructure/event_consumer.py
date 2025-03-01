import pulsar
import fastavro
from io import BytesIO
from pulsar.schema import Record, String, Integer, AvroSchema

class ResultCreatedSchema(Record):
    schema_version = String(default="1.0")
    result_id = Integer()
    patient = String()
    result = String()

class EventConsumer:
    def __init__(self, pulsar_url="pulsar://pulsar:6650"):
        self.client = pulsar.Client(pulsar_url)
        self.consumer = self.client.subscribe(
            "persistent://public/default/event-topic",
            subscription_name="event-subscription",
            schema=AvroSchema(ResultCreatedSchema)
        )

    def listen(self):
        print("Consumidor iniciado. Esperando eventos...")
        while True:
            try:
                msg = self.consumer.receive(timeout_millis=5000)
                event_data = msg.value()
                print(f"Evento recibido: {event_data}")

                self.consumer.acknowledge(msg)
            except pulsar.Timeout:
                print("No hay eventos en la cola. Reintentando...")
            except Exception as e:
                print(f"Error procesando evento: {str(e)}")
                self.consumer.negative_acknowledge(msg)

    def close(self):
        self.client.close()
