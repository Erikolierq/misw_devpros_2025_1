class EventPublisher:
    def publish(self, event):
        
        print(f"Evento publicado: {event.name} con datos: {event.data}")
