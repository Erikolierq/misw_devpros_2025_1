import pulsar
import json

class EventConsumer:
    def __init__(self, pulsar_url="pulsar://pulsar:6650"):
        self.client = pulsar.Client(pulsar_url)
        self.consumer = self.client.subscribe("persistent://public/default/event-topic", subscription_name="event-subscription")

    def listen(self):
        while True:
            msg = self.consumer.receive()
            try:
                event_data = json.loads(msg.data().decode("utf-8"))
                print(f"Evento recibido: {event_data}")
                self.consumer.acknowledge(msg)
            except Exception as e:
                print(f"Error procesando evento: {str(e)}")
                self.consumer.negative_acknowledge(msg)

    def close(self):
        self.client.close()
