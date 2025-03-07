from domain.events import ResultQueriedEvent, UserCreatedEvent
from infrastructure.event_store import EventStoreRepository
from infrastructure.repository import UserRepository
import json
from domain.user import User
import logging

class EventHandler:
    def __init__(self, repository: UserRepository, event_store: EventStoreRepository):
        self.repository = repository
        self.event_store = event_store

    def on_result_created(self, event: UserCreatedEvent):
        logging.info(f"Procesando evento: {event.name} - {event.data}")
        
        if self.event_store.is_event_processed(event):
            logging.info(f"Evento duplicado ignorado: {event.data['result_id']}")
            return
        
        self.repository.add(User(patient=event.data["patient"], result=event.data["result"]))
        self.event_store.mark_event_processed(event)

    def on_result_queried(self, event: ResultQueriedEvent):
        logging.info(f"Evento recibido: {event.name} - {event.data}")
        self.event_store.save_event(event)
