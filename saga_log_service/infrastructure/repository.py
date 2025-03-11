from infrastructure.database import db
from domain.saga_log import SagaLog

class SagaLogRepository:
    @staticmethod
    def save_log(topic, event_type, status, data):
        """
        Crea un nuevo log y lo guarda en la BD.
        """
        new_log = SagaLog(
            topic=topic,
            event_type=event_type,
            status=status,
            data=data
        )
        db.session.add(new_log)
        db.session.commit()

    @staticmethod
    def get_all_logs():
        """
        Retorna todos los registros, ordenados por fecha descendente
        """
        return SagaLog.query.order_by(SagaLog.created_at.desc()).all()
