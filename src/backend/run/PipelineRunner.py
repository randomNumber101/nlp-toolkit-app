from typing import Dict, List

from backend.events.backendEventApi import BackendEventApi
from backend.events.eventTransferObjects import StepState, StepLogUpdate, NotificationDomain, StepStatus
from backend.generaltypes import Pipeline, StepBlueprint, FrontendNotifier, Payload
from backend.register import Register
from backend.run.LogManager import LogManager, LogLevels, LoggerChannel


class FrontendChannel(LoggerChannel):

    def __init__(self, events: BackendEventApi, domain: NotificationDomain):
        self.events = events
        self.domain = domain

    def write(self, messages: List[str], level: LogLevels):
        logObject = StepLogUpdate(domain=self.domain, logs=messages)
        self.events.sendStepLogs(logObject)


class RunNotifier(FrontendNotifier):

    def __init__(self, logger: LogManager, events: BackendEventApi):
        super(RunNotifier, self).__init__()
        self.logger = logger
        self.events = events
        self.domain = None

    def log(self, message: str | List[str], level: LogLevels = LogLevels.DEBUG):
        self.logger.log(message, level)

    def sendStatus(self, stepState: StepState, progress: float):
        status = StepStatus(domain=self.domain, state=stepState, progress=progress)
        self.events.sendStepStatus(status)

    def withDomain(self, domain: NotificationDomain):
        self.domain = domain
        self.logger.setChannel("frontend", FrontendChannel(self.events, domain))
        return self


class PipelineRunner:

    def __init__(self, blueprints: Dict[str, StepBlueprint], pipeline: Pipeline, events: BackendEventApi,
                 logger: LogManager):
        self.blueprints = blueprints
        self.pipeline = pipeline
        self.events = events
        self.logger = logger

    def start(self, runId : str, input: str):
        # 1. Build frontend notifier
        notifier = RunNotifier(self.logger, self.events)

        # TODO: Add domain in frontend for general logs
        notifier.withDomain(NotificationDomain(runId, self.pipeline.id, 0))

        # 2. Create payload and initialize input data

        payload = Payload()

        # Find first csv parameter in first step
        blueprint_steps = [self.blueprints[stepVal.stepId] for stepVal in self.pipeline.steps]
        base_csv_type = Register.ParamTypeParser.parse("csv[]")

        first_csv_parameter = None
        for step in blueprint_steps:
            if first_csv_parameter:
                break
            for inputParameter in step.inOutDef.inputs_dynamic:
                if inputParameter.name == "data" and base_csv_type.transformableInto(inputParameter.type):
                    first_csv_parameter = inputParameter

        if not first_csv_parameter:
            notifier.log(f"Pipeline has no step that utilizes the input data. Input will thus be ignored", LogLevels.WARN)
        else:
            input_data_object = first_csv_parameter.type.parse(input) # Creates a pandas Dataframe object based on the headers
            payload.setData(input_data_object)

        # 3. Run step by step

        for step, stepVals in zip(blueprint_steps, self.pipeline.steps):
            # TODO: 1 - Initialize Step operation with static parameters and dynamic parameters
            # TODO: 2 - Call step operation
            # TODO: 3 - Set / Save Visualization, Save output
            # TODO: 4 - On Save : Trigger Success Event
            # TODO: 5 - Try/Errors : Trigger Failed event
            pass


        pass
