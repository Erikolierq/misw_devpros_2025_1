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

class UserCreatedEvent(DomainEvent):
    def __init__(self, user_id, username, role, version=1):
        super().__init__("UserCreated", {
            "id": user_id,
            "username": username,
            "role": role
        }, version)

class ResultQueriedEvent(DomainEvent):
    def __init__(self, user_id, query_result, version=1):
        super().__init__("ResultQueried", {
            "user_id": user_id,
            "query_result": query_result
        }, version)


