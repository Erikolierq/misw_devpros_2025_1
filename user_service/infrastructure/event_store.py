import json
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    data = Column(String, nullable=False)

class EventStore:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_event(self, event):
        session = self.Session()
        session.add(Event(event_type=event.type, version=event.version, data=json.dumps(event.data)))
        session.commit()
        session.close()
