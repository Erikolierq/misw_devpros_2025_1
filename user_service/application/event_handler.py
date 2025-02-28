from pulsar import Client
from infrastructure.event_store import EventStore
from domain.schemas import UserEventSchema

class EventHandler:
    def __init__(self, pulsar_url, db_url):
        self.event_store = EventStore(db_url)
        self.client = Client(pulsar_url)
        self.consumer = self.client.subscribe(
            'user_events', 
            'user-event-handler',
            schema=UserEventSchema
        )

    def listen(self):
        from app import db, User  # Importamos aquí para evitar el bucle de importación

        while True:
            msg = self.consumer.receive()
            try:
                event = msg.value()
                
                if event.type == "UserCreated":
                    self.event_store.save_event(event)

                    # Guardar usuario en la tabla `users`
                    session = self.event_store.Session()
                    user = User(
                        id=event.data.user_id,
                        username=event.data.username,
                        role=event.data.role
                    )
                    session.add(user)
                    session.commit()
                    session.close()

                self.consumer.acknowledge(msg)

            except Exception as e:
                print(f"Error procesando evento: {e}")
                self.consumer.negative_acknowledge(msg)
