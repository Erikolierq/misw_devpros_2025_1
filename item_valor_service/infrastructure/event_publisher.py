import pulsar
import json

class EventPublisher:
    def __init__(self, pulsar_client):
        self.client = pulsar_client
        try:
            self.producer = self.client.create_producer("persistent://public/default/event-topic")
        except Exception as e:
            print(f"Error creando el productor de eventos: {e}")
            raise

    def publish(self, event):
        try:
            event_data = json.dumps(event.to_dict()).encode('utf-8')
            print(f"Publicando evento en Pulsar: {json.dumps(event.data)}")
            self.producer.send(event_data)
            print(f"Evento publicado: {event.to_dict()}")
        except Exception as e:
            print(f"Error al publicar evento: {e}")

    def close(self):
        self.client.close()
