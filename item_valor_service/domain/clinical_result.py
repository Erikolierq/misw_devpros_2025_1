from infrastructure.database import db

class ClinicalResult(db.Model):
    __tablename__ = 'clinical_results'
    
    id = db.Column(db.Integer, primary_key=True)
    patient = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "patient": self.patient,
            "result": self.result
        }
