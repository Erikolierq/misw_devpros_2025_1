from domain.events import ResultQueriedEvent, ResultCreatedEvent
from infrastructure.event_store import EventStoreRepository
from infrastructure.repository import ClinicalResultRepository
import json

class EventHandler:
    def __init__(self, repository: ClinicalResultRepository, event_store: EventStoreRepository):
        self.repository = repository
        self.event_store = event_store

    def on_result_created(self, event: ResultCreatedEvent):
        print(f"Evento recibido: {event.name} - {event.data}")
        self.event_store.save_event(event.data["result_id"], event)

    def on_result_queried(self, event: ResultQueriedEvent):
        print(f"Evento recibido: {event.name} - {event.data}")
        self.event_store.save_event(event.data["result_id"], event)

    def process_pulsar_event(self, pulsar_client):
        consumer = pulsar_client.subscribe("persistent://public/default/event-topic", subscription_name="event-subscription")

        while True:
            msg = consumer.receive()
            event_data = json.loads(msg.data().decode("utf-8"))
            print(f"Mensaje recibido de Pulsar: {event_data}")
            
            if event_data.get("authorized", False):
                print(f"Autorizado para el resultado: {event_data['result_id']}")
            else:
                print(f"No autorizado para el resultado: {event_data['result_id']}")

            consumer.acknowledge(msg)
