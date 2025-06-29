import dataclasses
from typing import List, Optional

@dataclasses.dataclass
class MCQ:
    """
    Represents a multiple-choice question (MCQ) with options and an answer.
    """
    question: str
    options: List[str]
    answer: Optional[str] = None

    def __post_init__(self):
        if not self.options:
            raise ValueError("Options cannot be empty.")
        if self.answer and self.answer not in self.options:
            raise ValueError("Answer must be one of the provided options.")
    
    def __str__(self):
        return f"Question: {self.question}\nOptions: {', '.join(self.options)}\nAnswer: {self.answer}"
