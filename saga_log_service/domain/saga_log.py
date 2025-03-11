from datetime import datetime
from infrastructure.database import db

class SagaLog(db.Model):
    __tablename__ = "saga_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(255), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="RECEIVED")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "event_type": self.event_type,
            "status": self.status,
            "data": self.data,
            "created_at": self.created_at.isoformat()
        }
