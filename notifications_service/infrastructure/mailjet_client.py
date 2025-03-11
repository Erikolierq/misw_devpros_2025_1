import os
import logging
from mailjet_rest import Client

class MailjetClient:
    def __init__(self):
        
        self.api_key = os.getenv("MJ_APIKEY_PUBLIC", "8233f356a53b1981eb40b8dcb9b0d253").strip()
        self.api_secret = os.getenv("MJ_APIKEY_PRIVATE", "9887974ee043a7333a7f472f36f51a21").strip()
        self.default_sender = os.getenv("MAILJET_DEFAULT_SENDER", "fangeruno@gmail.com").strip()

        logging.info(f"[MailjetClient] Cargando credenciales API...")
        logging.info(f" MAILJET_API_KEY: {'OK' if self.api_key else 'FALTANTE'}")
        logging.info(f" MAILJET_API_SECRET: {'OK' if self.api_secret else 'FALTANTE'}")
        logging.info(f" MAILJET_DEFAULT_SENDER: {self.default_sender}")

        if not self.api_key or not self.api_secret:
            logging.error("[MailjetClient]  Faltan credenciales API.")
            return

        self.mailjet = Client(auth=(self.api_key, self.api_secret), version='v3.1')

    def send_email(self, subject: str, content: str):
        if not self.api_key or not self.api_secret:
            logging.error("[MailjetClient]  Faltan credenciales API. No se puede enviar el correo.")
            return

        data = {
            'Messages': [
                {
                    "From": {
                        "Email": self.default_sender,
                        "Name": "Plataforma Notificaciones"
                    },
                    "To": [
                        {
                            "Email": "erik.o.q@gmail.com"
                        }
                    ],
                    "Subject": subject,
                    "TextPart": content
                }
            ]
        }

        logging.info("[MailjetClient]  Enviando correo...")
        result = self.mailjet.send.create(data=data)

        logging.info(f"[MailjetClient]  Respuesta de Mailjet: {result.status_code} - {result.text}")

        if result.status_code != 200:
            logging.error(f"[MailjetClient]  Error al enviar: {result.status_code} - {result.text}")
        else:
            logging.info("[MailjetClient]  Correo enviado exitosamente.")
