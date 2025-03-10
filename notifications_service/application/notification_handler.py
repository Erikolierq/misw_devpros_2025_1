# notifications_service/application/notification_handler.py
import logging
from infrastructure.mailjet_client import MailjetClient

class NotificationHandler:
    def __init__(self):
        self.mailjet_client = MailjetClient()

    def handle_user_created(self, event_data):
        """
        Lógica para notificar cuando se crea un usuario en JSON (dict).
        event_data:
          {
            "id": 4,
            "username": "usuario2",
            "role": 1,
            ...
          }
        """
        user_id = event_data.get("id")
        username = event_data.get("username")
        role = event_data.get("role")

        logging.info(f"[NotificationHandler] Procesando evento -> user_id={user_id}, username={username}, role={role}")
        print("==> Iniciando envío de correo...")

        subject = "¡Bienvenido a la plataforma!"
        body = f"Hola {username}, tu usuario (ID={user_id}) se creó con éxito (role={role})."

        try:
            self.mailjet_client.send_email(subject=subject, content=body)
            logging.info(f"[NotificationHandler] Correo de bienvenida enviado a {username}.")
            print(f"Correo enviado con asunto: '{subject}' al usuario: {username}")
        except Exception as e:
            logging.error(f"[NotificationHandler] Error enviando correo a {username}: {str(e)}")
            print(f"Error enviando correo a {username}: {str(e)}")
