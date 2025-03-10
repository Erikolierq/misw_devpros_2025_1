from pulsar.schema import Record, String, Integer, AvroSchema

class ResultCreatedSchema(Record):
    schema_version = String(default="1.0")
    id = Integer()
    username = String()
    password = String()
    role = Integer()
