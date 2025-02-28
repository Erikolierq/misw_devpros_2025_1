import json
import datetime

class DomainEvent:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.timestamp = datetime.datetime.utcnow().isoformat()

    def to_json(self):
        return json.dumps({
            "name": self.name,
            "data": self.data,
            "timestamp": self.timestamp
        })

class ResultCreatedEvent(DomainEvent):
    def __init__(self, result_id, patient, result_text):
        super().__init__("ResultCreated", {
            "result_id": result_id,
            "patient": patient,
            "result": result_text
        })

class ResultQueriedEvent(DomainEvent):
    def __init__(self, user_id, result_id):
        super().__init__("ResultQueried", {
            "user_id": user_id,
            "result_id": result_id
        })
