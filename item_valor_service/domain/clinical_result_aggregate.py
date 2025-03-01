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

    @staticmethod
    def rehydrate(event_store_repo, result_id):
        events = event_store_repo.get_events_for_aggregate(result_id)
        if not events:
            return None

        aggregate = None
        for event in events:
            if event["name"] == "ResultCreated":
                aggregate = ClinicalResultAggregate(event["data"]["patient"], event["data"]["result"])
        
        return aggregate
