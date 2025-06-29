import dataclasses

@dataclasses.dataclass
class Essay:
    """
    Represents an essay question with a prompt and an optional answer.
    """
    question: str
    answer: str = ""

    def __post_init__(self):
        if not self.question:
            raise ValueError("Question cannot be empty.")
        if len(self.question) < 10:
            raise ValueError("Question must be at least 10 characters long.")

