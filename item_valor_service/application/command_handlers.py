from domain.clinical_result import ClinicalResult
from domain.events import ResultCreatedEvent
from infrastructure.repository import ClinicalResultRepository
from infrastructure.event_publisher import EventPublisher
from infrastructure.event_store import EventStoreRepository

class CommandHandler:
    def __init__(self, repository: ClinicalResultRepository, publisher: EventPublisher, event_store: EventStoreRepository):
        self.repository = repository
        self.publisher = publisher
        self.event_store = event_store

    def handle_create_result(self, patient, result_text):
        if not patient or not result_text:
            raise ValueError("Faltan campos requeridos")

        new_result = ClinicalResult(patient=patient, result=result_text)
        self.repository.add(new_result)

        event = ResultCreatedEvent(new_result.id, patient, result_text)
        self.event_store.save_event(event) 
        self.publisher.publish(event)

        return new_result.to_dict()
