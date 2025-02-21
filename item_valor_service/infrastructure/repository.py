from domain.clinical_result import ClinicalResult

class ClinicalResultRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, result_id):
        return self.session.query(ClinicalResult).get(result_id)

    def add(self, clinical_result):
        self.session.add(clinical_result)
        self.session.commit()
