from infrastructure.database import db
from datetime import datetime
import pulsar
import json

class EventStore(db.Model):
    __tablename__ = 'event_store'
    
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventStoreRepository:
    def __init__(self, db_session):
        self.db_session = db_session
        self.client = pulsar.Client("pulsar://pulsar:6650")

    def save_event(self, event):

        new_event = EventStore(event_name=event.name, event_data=event.data)
        self.db_session.add(new_event)
        self.db_session.commit()

        producer = self.client.create_producer("persistent://public/default/event-topic")
        producer.send(json.dumps(event.data).encode('utf-8'))

    def close(self):
        self.client.close()

