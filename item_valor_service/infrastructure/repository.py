from domain.clinical_result import ClinicalResult
from infrastructure.encryption_service import EncryptionService

class ClinicalResultRepository:
    def __init__(self, session):
        self.session = session
        self.encryption_service = EncryptionService()

    def get_by_id(self, result_id):
        result = self.session.query(ClinicalResult).get(result_id)
        if result:
            result.result = self.encryption_service.decrypt(result.result)
        return result

    def add(self, clinical_result):
        clinical_result.result = self.encryption_service.encrypt(clinical_result.result)
        self.session.add(clinical_result)
        self.session.commit()
