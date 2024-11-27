import os.path
import uuid

from backend.events.backendEventApi import BackendEventApi
from backend.run.LogManager import LogManager, LogLevels
from backend.run.PipelineRunner import PipelineRunner
from backend.storage.storageApi import PipelineApi, StorageApi



class RunStorageApi:

    def __init__(self, logger, run_directory):
        self.log = logger
        self.directory = run_directory

    def initializeRun(self, run_id):
        path = os.path.join(self.directory, run_id)
        if os.path.isdir(path):
            self.log(f"Cannot initialize run {run_id}. Run already exists.", LogLevels.ERROR)
            return False
        os.makedirs(path)
        return True


    def getStatus(self, run_id, stepId):
        pass

    def writeStatus(self, run_id, status):
        pass

    def getResult(self, run_id):
        pass

    def writeResult(self, run_id, result):
        pass

    def getRunStatus(self, run_id):
        pass



class RunApi:

    def __init__(self, storage: StorageApi, events: BackendEventApi):
        self.runs_dir = storage.PATHS.runs
        self.pipelineApi = storage.PIPELINES
        self.stepApi = storage.STEPS
        self.eventApi = events
        self.logger = LogManager()


    def invokeEvent(self, name, data_object):
        self.eventApi.sendEvent(name, data_object)

    # Returns a new run id
    def startRun(self, pipelineId, input: str) -> str:
        runId = str(uuid.uuid4())
        pipeline = self.pipelineApi.load_pipeline(pipelineId)
        blueprints = {bp.stepId: bp for bp in self.stepApi.load_all()}

        runner = PipelineRunner(blueprints, pipeline, )

        return runId

