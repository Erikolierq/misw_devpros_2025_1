from domain.user_aggregate import UserAggregate
from domain.events import UserCreatedEvent
from infrastructure.repository import UserRepository
from infrastructure.event_publisher import EventPublisher
from infrastructure.event_store import EventStoreRepository

class CommandHandler:
    def __init__(self, repository: UserRepository, publisher: EventPublisher, event_store: EventStoreRepository):
        self.repository = repository
        self.publisher = publisher
        self.event_store = event_store

    def handle_create_result(self, username, password, role):
        try:
            if not username or not password:
                raise ValueError("Faltan campos requeridos")

            aggregate = UserAggregate.create(username, password, role)

            self.repository.add(aggregate.user) 

            event = UserCreatedEvent(aggregate.user.id, username, role)
            self.event_store.save_event(event)
            self.publisher.publish(event)

            return aggregate.user.to_dict()

        except Exception as e:
            print(f"Error en handle_create_result: {str(e)}")
            raise


