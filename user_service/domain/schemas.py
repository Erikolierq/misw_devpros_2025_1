from pulsar.schema import JsonSchema, Record, String, Integer

class UserCommandData(Record):
    username = String()
    password = String()
    role = Integer()

class UserCommandSchema(Record):
    type = String()
    version = Integer()
    data = UserCommandData()

class UserEventData(Record):
    user_id = String()
    username = String()
    role = Integer()

class UserEventSchema(Record):
    type = String()
    version = Integer()
    data = UserEventData()  
