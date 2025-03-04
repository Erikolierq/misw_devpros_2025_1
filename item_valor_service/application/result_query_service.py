from domain.events import ResultQueriedEvent

class ResultQueryService:
    def __init__(self, repository, event_publisher):
        self.repository = repository
        self.event_publisher = event_publisher

    def get_result(self, result_id, user):
        clinical_result = self.repository.get_by_id(result_id)
        if clinical_result:
            event = ResultQueriedEvent(user_id=user.get('id'), result_id=result_id)
            self.event_publisher.publish(event)
            return clinical_result.to_dict()
        return None
