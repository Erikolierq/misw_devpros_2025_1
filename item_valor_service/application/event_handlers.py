from domain.events import ResultQueriedEvent, ResultCreatedEvent
from infrastructure.event_store import EventStoreRepository
from infrastructure.repository import ClinicalResultRepository
import json
from domain.clinical_result import ClinicalResult
import logging

class EventHandler:
    def __init__(self, repository: ClinicalResultRepository, event_store: EventStoreRepository):
        self.repository = repository
        self.event_store = event_store

    def on_result_created(self, event: ResultCreatedEvent):
        logging.info(f"Procesando evento: {event.name} - {event.data}")
        
        if self.event_store.is_event_processed(event):
            logging.info(f"Evento duplicado ignorado: {event.data['result_id']}")
            return
        
        self.repository.add(ClinicalResult(patient=event.data["patient"], result=event.data["result"]))
        self.event_store.mark_event_processed(event)

    def on_result_queried(self, event: ResultQueriedEvent):
        logging.info(f"Evento recibido: {event.name} - {event.data}")
        self.event_store.save_event(event)
