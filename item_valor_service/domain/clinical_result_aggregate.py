from .clinical_result import ClinicalResult
from .events import ResultCreatedEvent

class ClinicalResultAggregate:
    def __init__(self, patient, result):
        self.clinical_result = ClinicalResult(patient=patient, result=result)

    @staticmethod
    def create(patient, result):
        return ClinicalResultAggregate(patient, result)

    def to_dict(self):
        return {
            "id": self.clinical_result.id,
            "patient": self.clinical_result.patient,
            "result": self.clinical_result.result
        }
