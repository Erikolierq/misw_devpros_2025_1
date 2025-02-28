from domain.clinical_result_aggregate import ClinicalResultAggregate
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
        try:
            if not patient or not result_text:
                raise ValueError("Faltan campos requeridos")

            aggregate = ClinicalResultAggregate.create(patient, result_text)

            self.repository.add(aggregate.clinical_result)

            event = ResultCreatedEvent(aggregate.clinical_result.id, patient, result_text)
            self.event_store.save_event(event)
            self.publisher.publish(event)

            return aggregate.clinical_result.to_dict()

        except Exception as e:
            print(f"Error en handle_create_result: {str(e)}")
            raise

