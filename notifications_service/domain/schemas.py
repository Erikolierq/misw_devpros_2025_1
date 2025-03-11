# notifications_service/domain/schemas.py
from pulsar.schema import Record, String, Integer, AvroSchema

class UserCreatedSchema(Record):
    """
    Esquema Avro para el evento de usuario creado.
    Coincide con la estructura que tu microservicio de usuarios publica.
    """
    schema_version = String(default="1.0")
    id = Integer()        # ID del usuario
    username = String()   # Nombre de usuario o correo
    password = String()   # Contraseña (encriptada o no)
    role = Integer()      # Rol asignado

class ResultCreatedSchema(Record):
    """
    Esquema Avro para el evento de resultado médico creado.
    Coincide con la estructura que tu item_valor_service publica.
    """
    schema_version = String(default="1.0")
    result_id = Integer()  # ID del resultado
    patient = String()     # Nombre del paciente
    result = String()      # Resultado (ej: "Negativo", "Positivo", "N/A")
