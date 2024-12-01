import json
import os.path
import threading
import uuid

import pandas

from backend.events.backendEventApi import BackendEventApi
from backend.generaltypes import Pipeline
from backend.run.LogManager import LogManager, LogLevels
from backend.run.PipelineRunner import PipelineRunner
from backend.storage.storageApi import PipelineApi, StorageApi
from backend.transferObjects.pipelineTransferObjects import convert_pipeline_to_transfer
from backend.transferObjects.visualization import Visualization


class RunStorageApi:

    def __init__(self, run_directory):
        self.directory = run_directory

    def initializeRun(self, run_id, pipeline : Pipeline):
        base_path = os.path.join(self.directory, run_id)
        viz_path = os.path.join(base_path, "visualizations")
        os.makedirs(viz_path)

        # Save the original pipeline, so it can be reconstructed
        original_pipeline = convert_pipeline_to_transfer(pipeline).to_dict()
        pipe_path = os.path.join(base_path, "original_pipeline.json")
        with open(pipe_path, 'w') as f:
            json.dump(original_pipeline, f, indent=4)

        return True

    def getRunPipeline(self, run_id):
        base_path = os.path.join(self.directory, run_id)
        pipe_path = os.path.join(base_path, "original_pipeline.json")
        if os.path.isfile(pipe_path):
            with open(pipe_path, 'r') as f:
                pipe_json = json.load(f)
            return pipe_json
        raise FileNotFoundError("No result has been saved yet. Make sure that the run has finished.")

    def saveVisualization(self, run_id, stepIndex: int, viz: Visualization):
        base_path = os.path.join(self.directory, run_id, "visualizations")
        viz_path = os.path.join(base_path, f"{stepIndex}.json")
        with open(viz_path, 'w') as f:
            json.dump(viz.toJson(), f, indent=4)
        return True

    def getVisualization(self, run_id, stepIndex: int) -> dict:
        base_path = os.path.join(self.directory, run_id)
        viz_path = os.path.join(base_path, f"{stepIndex}.json")
        with open(viz_path, 'w') as f:
            viz_json = json.load(f)
        return viz_json

    def saveResult(self, run_id, data: pandas.DataFrame):
        base_path = os.path.join(self.directory, run_id)
        save_path = os.path.join(base_path, "result.pkl")
        return data.to_pickle(save_path)

    def getResult(self, run_id):
        base_path = os.path.join(self.directory, run_id)
        save_path = os.path.join(base_path, "result.pkl")
        if os.path.isfile(save_path):
            return pandas.read_pickle(save_path)
        raise FileNotFoundError("No result has been saved yet. Make sure that the run has finished.")


class RunApi:

    def __init__(self, storage: StorageApi, events: BackendEventApi):
        self.runs_dir = storage.PATHS.runs
        self.pipelineApi = storage.PIPELINES
        self.stepApi = storage.STEPS
        self.runStorageApi = RunStorageApi(run_directory=self.runs_dir)
        self.eventApi = events


    def invokeEvent(self, name, data_object):
        self.eventApi.sendEvent(name, data_object)

    '''
    Starts the new run in a separate Thread and returns its identifier (run_id)
    '''
    def startRun(self, pipelineId, input_data: str) -> str:
        run_id = f"{pipelineId}-{str(uuid.uuid4())[:18]}"

        def runStep():
            pipeline = self.pipelineApi.load_pipeline(pipelineId)
            blueprints = {bp.stepId: bp for bp in self.stepApi.load_all()}
            runner = PipelineRunner(self.eventApi, self.runStorageApi)
            runner.start(blueprints, pipeline, run_id, input_data)

        runThread = threading.Thread(target=runStep, name=f"StepRunner for {run_id}", daemon=False)
        runThread.start()

        return run_id

