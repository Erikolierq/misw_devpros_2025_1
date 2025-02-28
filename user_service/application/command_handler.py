import uuid
from pulsar import Client
from pulsar.schema import JsonSchema  # ✅ Importa JsonSchema
from domain.user import User
from domain.schemas import UserCommandSchema, UserEventSchema

class CommandHandler:
    def __init__(self, pulsar_url):
        self.client = Client(pulsar_url)
        
        self.consumer = self.client.subscribe(
            'user_commands', 
            'user-service',
            schema=JsonSchema(UserCommandSchema)  # ✅ Corrige el esquema
        )

        self.producer = self.client.create_producer(
            'user_events',
            schema=JsonSchema(UserEventSchema)  # ✅ Corrige el esquema
        )

    def listen(self):
        while True:
            msg = self.consumer.receive()
            try:
                command = msg.value()
                if command.type == "CreateUser":
                    self.handle_create_user(command.data)
                self.consumer.acknowledge(msg)
            except Exception as e:
                print(f"Error procesando comando: {e}")
                self.consumer.negative_acknowledge(msg)

    def handle_create_user(self, data):
        user = User(user_id=str(uuid.uuid4()), **data)
        event = user.create_event()

        # ✅ Serializa el evento antes de enviarlo
        self.producer.send(event)
