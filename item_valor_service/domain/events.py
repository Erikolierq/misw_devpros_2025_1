import json
import datetime

class DomainEvent:
    def __init__(self, name, data, version=1):
        self.name = name
        self.data = data
        self.version = version
        self.timestamp = datetime.datetime.utcnow().isoformat()

    def to_json(self):
        return json.dumps({
            "name": self.name,
            "data": self.data,
            "version": self.version,
            "timestamp": self.timestamp
        })

class ResultCreatedEvent(DomainEvent):
    def __init__(self, result_id, patient, result_text, version=1):
        super().__init__("ResultCreated", {
            "result_id": result_id,
            "patient": patient,
            "result": result_text
        }, version)

class ResultQueriedEvent(DomainEvent):
    def __init__(self, user_id: str, query_result: dict):
        self.user_id = user_id
        self.query_result = query_result 

