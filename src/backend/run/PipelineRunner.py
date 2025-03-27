import traceback
from typing import Dict, List, Union

from backend.run.backendEventApi import BackendEventApi
from backend.transferObjects.eventTransferObjects import StepState, StepLogUpdate, NotificationDomain, StepStatus, Log, \
    LogLevels
from backend.register import Register
from backend.run.LogManager import LogManager, LoggerChannel, StatusManager, StatusChannel
from backend.transferObjects.visualization import MultiVisualization
from backend.types.blueprint import StepBlueprint
from backend.types.frontendNotifier import FrontendNotifier
from backend.types.payload import Payload
from backend.types.pipeline import Pipeline


class FrontendLogChannel(LoggerChannel):

    def __init__(self, events: BackendEventApi, domain: NotificationDomain):
        self.events = events
        self.domain = domain
        super(FrontendLogChannel, self).__init__()

    def handle(self, obj: Dict[str, Union[str, LogLevels]]):
        messages: List[str] = obj.get("messages", [])
        level: LogLevels = obj.get("level", LogLevels.INFO)
        logMessages = [Log(level, message) for message in messages]
        self.events.sendStepLogs(StepLogUpdate(self.domain, logMessages))


class FrontendStatusChannel(StatusChannel):
    def __init__(self, events: BackendEventApi, domain: NotificationDomain):
        self.events = events
        self.domain = domain
        super(FrontendStatusChannel, self).__init__()

    def handle(self, status: StepStatus):
        self.events.sendStepStatus(status)


class RunNotifier(FrontendNotifier):

    def __init__(self, events: BackendEventApi):
        super(RunNotifier, self).__init__()
        self.events = events
        self.logger = LogManager()
        self.logger.set_channel("console", LoggerChannel()) # Always also log to console
        self.status_manager = StatusManager()
        self.domain = None

    def log(self, message: str | List[str], level: LogLevels = LogLevels.DEBUG):
        self.logger.log(message, level)

    def sendStatus(self, stepState: StepState, progress: float = 0):
        status = StepStatus(domain=self.domain, state=stepState, progress=progress)
        self.status_manager.send_status(status)

    def withDomain(self, domain: NotificationDomain):
        self.domain = domain
        self.logger.set_channel("frontend", FrontendLogChannel(self.events, domain))
        self.status_manager.set_channel("frontend", FrontendStatusChannel(self.events, domain))
        return self


class PipelineRunner:

    def __init__(self, events: BackendEventApi, runStorage: "RunStorageApi"):
        self.events = events
        self.storage = runStorage


    def __call__(self, *args, **kwargs):
        self.start(*args, **kwargs)

    def start(self, blueprints: Dict[str, StepBlueprint], pipeline: Pipeline, run_id: str, input: str):

        # 0. Create folder structure
        self.storage.initializeRun(run_id, pipeline)

        # 1. Build frontend notifier
        notifier = RunNotifier(self.events)

        # TODO: Add domain in frontend for general logs
        notifier.withDomain(NotificationDomain(run_id, pipeline.id, 0))

        # 2. Create payload and initialize input data

        payload = Payload()

        # Find first csv parameter in first step
        blueprint_steps = [blueprints[stepVal.stepId] for stepVal in pipeline.steps]
        base_csv_type = Register.ParamTypeParser.parse("csv[]")

        first_csv_parameter = None
        for step in blueprint_steps:
            if first_csv_parameter:
                break
            for inputParameter in step.inOutDef.inputs_dynamic:
                if inputParameter.name == "data" and base_csv_type.transformableInto(inputParameter.type):
                    first_csv_parameter = inputParameter

        if not first_csv_parameter:
            notifier.log(f"Pipeline has no step that utilizes the input data. Input will thus be ignored",
                         LogLevels.WARN)
        else:
            input_data_object = first_csv_parameter.type.parse(
                input)  # Creates a pandas Dataframe object based on the headers
            payload.original_data = input_data_object
            payload.data = input_data_object

        # 3. Run step by step

        stepIndex = 0
        for step, stepVals in zip(blueprint_steps, pipeline.steps):
            notifier.withDomain(NotificationDomain(run_id, pipeline.id, stepIndex))
            try:
                result = step.run(stepVals, payload, notifier)
            except Exception as e:
                traceback_str = traceback.format_exc()
                notifier.log(traceback_str, LogLevels.ERROR)
                notifier.log(f"Backend exception during run: {repr(e)}", LogLevels.ERROR)
                notifier.sendStatus(StepState.FAILED)
                return

            if not result or result == StepState.FAILED:
                notifier.sendStatus(StepState.FAILED)
                return

            visualizations = payload.popVisualizations()
            print(f"Got visualizations: {len(visualizations)}")
            if len(visualizations) == 1:
                self.storage.saveVisualization(run_id, stepIndex, visualizations[0])
            elif len(visualizations) > 1:
                allVisualizations = MultiVisualization(visualizations)
                self.storage.saveVisualization(run_id, stepIndex, allVisualizations)

            if stepIndex == len(blueprint_steps) - 1:
                # Last step finished, save the latest data object to filesystem
                result = payload.data
                if result is not None:
                    self.storage.saveResult(run_id, result)
                notifier.log(f"Finished processing last step. Saved result to file.", LogLevels.INFO)
            else:
                notifier.log(f"Finished processing step {stepIndex}.", LogLevels.INFO)

            notifier.sendStatus(StepState.SUCCESS, 100)
            stepIndex += 1
