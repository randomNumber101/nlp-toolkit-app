from typing import Dict

from backend.generaltypes import Pipeline, StepBlueprint
from backend.run.LogManager import LogManager


class PipelineRunner:

    def __init__(self, blueprints: Dict[str, StepBlueprint], pipeline: Pipeline, logger: LogManager):
        self.blueprints = blueprints
        self.pipeline = pipeline
        self.logger = logger


    def start(self, input: str):

        # 1. Build frontend notifier

        # 1.1 - logger : passed in
        # 1.2 - status printer : ?

        # 2. Parse payload from input

        # 2.



        pass






