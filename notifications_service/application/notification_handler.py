# notifications_service/application/notification_handler.py
import logging
from infrastructure.mailjet_client import MailjetClient

class NotificationHandler:
    def __init__(self):
        self.mailjet_client = MailjetClient()

    def handle_user_created(self, event_data):
        # ... (ya existente, para usuarios)
        user_id = event_data.get("id")
        username = event_data.get("username")
        role = event_data.get("role")

        logging.info(f"[NotificationHandler] Procesando USER -> user_id={user_id}, username={username}, role={role}")
        print("==> Iniciando envío de correo de bienvenida")

        subject = "¡Bienvenido a la plataforma!"
        body = f"Hola {username}, tu usuario (ID={user_id}) se creó con éxito (role={role})."

        try:
            self.mailjet_client.send_email(subject=subject, content=body)
            logging.info(f"[NotificationHandler] Correo de bienvenida enviado a {username}.")
        except Exception as e:
            logging.error(f"[NotificationHandler] Error enviando correo a {username}: {str(e)}")

    def handle_result_created(self, event_data):
        """
        Lógica para notificar cuando se crea un resultado médico.
        event_data podría ser algo como:
          {
            "id": 3,
            "patient": "Nombre Paciente",
            "result": "Resultado X",
            ...
          }
        """
        logging.info("[NotificationHandler] Procesando RESULT -> Creación de un resultado médico")
        
        # Ajusta según cómo tu item_valor_service envíe el JSON
        result_id = event_data.get("id")        # o "result_id" si se llama así
        patient = event_data.get("patient")
        result_value = event_data.get("result")

        subject = "Nuevo resultado médico"
        body = (f"Hola {patient},\n"
                f"Te informamos que se ha creado un nuevo resultado médico con ID={result_id}.\n"
                f"El resultado es: {result_value}")

        try:
            self.mailjet_client.send_email(subject=subject, content=body)
            logging.info(f"[NotificationHandler] Correo de resultado enviado a {patient}.")
        except Exception as e:
            logging.error(f"[NotificationHandler] Error enviando correo de resultado a {patient}: {str(e)}")
