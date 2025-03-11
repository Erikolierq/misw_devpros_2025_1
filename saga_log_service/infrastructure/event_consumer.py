import logging
import pulsar

class SagaLogConsumer:
    """
    Consumidor genérico (similar al EventConsumer de notifications_service),
    pero orientado a guardar logs en la BD a través de SagaEventHandler.
    """
    def __init__(self, pulsar_client, topic, subscription_name, event_handler):
        self.client = pulsar_client
        self.topic = topic
        self.subscription_name = subscription_name
        self.event_handler = event_handler

        self.consumer = self.client.subscribe(
            topic=self.topic,
            subscription_name=self.subscription_name,
            consumer_type=pulsar.ConsumerType.Shared
        )

    def listen(self):
        logging.info(f"[SagaLogConsumer] Escuchando eventos en {self.topic} ...")
        while True:
            msg = None
            try:
                msg = self.consumer.receive(timeout_millis=5000)
                if msg:
                    topic_name = msg.topic_name()
                    # Invocar el handler que procesará y guardará en BD
                    self.event_handler.process_event(topic_name, msg)
                    self.consumer.acknowledge(msg)
                    logging.info(f"[SagaLogConsumer] ✅ Mensaje ACK en {topic_name}")

            except pulsar.Timeout:
                # No hay mensajes, se continúa
                continue

            except Exception as e:
                logging.error(f"[SagaLogConsumer] ❌ Error procesando evento: {str(e)}")
                if msg:
                    self.consumer.negative_acknowledge(msg)
