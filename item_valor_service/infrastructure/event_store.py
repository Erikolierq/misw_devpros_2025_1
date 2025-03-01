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
   processed = db.Column(db.Boolean, default=False)

class EventStoreRepository:
   def __init__(self, db_session):
       self.db_session = db_session
       self.client = pulsar.Client("pulsar://pulsar:6650")

   def save_event(self, event):
       new_event = EventStore(event_name=event.name, event_data=event.data, processed=False)
       self.db_session.add(new_event)
       self.db_session.commit()

       try:
           producer = self.client.create_producer("persistent://public/default/event-topic")
           producer.send(json.dumps(event.data).encode('utf-8'))
           new_event.processed = True 
           self.db_session.commit()
       except Exception as e:
           print(f"Error al publicar evento: {e}")

   def get_unprocessed_events(self):
       return self.db_session.query(EventStore).filter_by(processed=False).all()


