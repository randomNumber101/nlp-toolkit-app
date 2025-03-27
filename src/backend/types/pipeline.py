from typing import List

from backend.types.blueprint import StepValues


class Pipeline:
    def __init__(self, id, name, description="", information=None, steps: List[StepValues] = None, tags: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.information = information
        if steps is None:
            steps = []
        self.steps = steps
        self.tags = tags