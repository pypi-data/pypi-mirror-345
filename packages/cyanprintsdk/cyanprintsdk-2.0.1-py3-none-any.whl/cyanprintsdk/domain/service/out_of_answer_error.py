from cyanprintsdk.domain.core.question import Question


class OutOfAnswerException(Exception):
    def __init__(self, message: str, question: Question):
        super().__init__(message)
        self.question = question
