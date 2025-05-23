import json
import os.path
import shutil
import threading
import uuid
from tkinter import filedialog

import pandas

from backend.run.backendEventApi import BackendEventApi
from backend.types.pipeline import Pipeline
from backend.run.PipelineRunner import PipelineRunner
from backend.storage.storageApi import StorageApi
from backend.transferObjects.pipelineTransferObjects import convert_pipeline_to_transfer
from backend.transferObjects.visualization import Visualization




class RunStorageApi:

    PREVIEW_ROWS_NUM = 150
    MAX_RUNS = 10

    def __init__(self, run_directory):
        self.directory = run_directory

    def initializeRun(self, run_id, pipeline : Pipeline):
        self.recycleRuns()
        base_path = os.path.join(self.directory, run_id)
        viz_path = os.path.join(base_path, "visualizations")
        os.makedirs(viz_path)

        # Save the original pipeline, so it can be reconstructed
        original_pipeline = convert_pipeline_to_transfer(pipeline).to_dict()
        pipe_path = os.path.join(base_path, "original_pipeline.json")
        with open(pipe_path, 'w') as f:
            json.dump(original_pipeline, f, indent=4)

        return True


    def getRunIds(self):
        """
            Returns a list of all run ids in the storage directory sorted by modification date. (newest first)
        """
        run_ids = [f for f in os.listdir(self.directory) if os.path.isdir(os.path.join(self.directory, f))]
        run_ids = sorted(run_ids, key=lambda x: self.getModificationDate(x), reverse=True)
        return run_ids

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
        base_path = os.path.join(self.directory, run_id, "visualizations")
        viz_path = os.path.join(base_path, f"{stepIndex}.json")
        with open(viz_path, 'r') as f:
            viz_json = json.load(f)
        return viz_json

    def saveResult(self, run_id, data: pandas.DataFrame):
        base_path = os.path.join(self.directory, run_id)
        save_path = os.path.join(base_path, "result.csv")

        # Delete oldest runs if there are too many
        return data.to_csv(save_path)

    def getResultPath(self, run_id):
        base_path = os.path.join(self.directory, run_id)
        save_path = os.path.join(base_path, "result.csv")
        if os.path.isfile(save_path):
            return save_path
        raise FileNotFoundError("No result has been saved yet. Make sure that the run has finished.")

    def getResult(self, run_id) -> pandas.DataFrame:
        save_path = self.getResultPath(run_id)
        return pandas.read_csv(save_path, nrows=RunStorageApi.PREVIEW_ROWS_NUM)

    def getModificationDate(self, run_id):
        base_path = os.path.join(self.directory, run_id)
        return os.path.getmtime(base_path)

    def delete_run(self, run_id):
        base_path = os.path.join(self.directory, run_id)
        if os.path.isdir(base_path):
            shutil.rmtree(base_path)
            return True

    def recycleRuns(self):
        run_ids = self.getRunIds()
        if len(run_ids) > RunStorageApi.MAX_RUNS:
            for run_id in run_ids[RunStorageApi.MAX_RUNS:]:
                self.delete_run(run_id)



class RunApi:

    def __init__(self, storage: StorageApi, events: BackendEventApi):
        self.runs_dir = storage.PATHS.runs
        self._pipelineApi = storage.PIPELINES
        self._stepApi = storage.STEPS
        self._runStorageApi = RunStorageApi(run_directory=self.runs_dir)
        self._eventApi = events


    def invokeEvent(self, name, data_object):
        self._eventApi.sendEvent(name, data_object)

    '''
    Starts the new run in a separate Thread and returns its identifier (run_id)
    '''
    def startRun(self, pipelineId, input_handle) -> str:

        # Convert to csv as default
        input_data = input_handle["data"]
        if input_handle["type"] == "text":
            input_data = "text\n" + input_data

        run_id = f"{pipelineId}-{str(uuid.uuid4())[:18]}"

        def runStep():
            pipeline = self._pipelineApi.load_pipeline(pipelineId)
            blueprints = {bp.stepId: bp for bp in self._stepApi.load_all()}
            runner = PipelineRunner(self._eventApi, self._runStorageApi)
            runner.start(blueprints, pipeline, run_id, input_data)

        runThread = threading.Thread(target=runStep, name=f"StepRunner for {run_id}", daemon=True)
        runThread.start()

        return run_id


    def getVisualization(self, run_id, stepIndex: int):
        return self._runStorageApi.getVisualization(run_id, stepIndex)

    def getResult(self, run_id):
        dataframe = self._runStorageApi.getResult(run_id)
        return dataframe.to_json(orient='records')

    def getOriginalPipeline(self, run_id):
        return self._runStorageApi.getRunPipeline(run_id)



    def saveResult(self, run_id):
        # Open the file save dialog; this will block until the user selects a location.
        file_path = filedialog.asksaveasfilename(
            title="Save CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            # Copy file to location
            result_path = self._runStorageApi.getResultPath(run_id)
            shutil.copyfile(result_path, file_path)
            return None
        else:
            raise IOError("No file selected.")
