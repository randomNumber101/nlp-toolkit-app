import os
import json

from src.backend.storage.parsing import StepBlueprintParser

from ..register import Register


class Paths:
    def __init__(self):
        self.storage = os.path.dirname(__file__)
        self.pipelines = os.path.join(self.storage, "pipelines")
        self.steps = os.path.join(self.storage, "steps")


def list_jsons(path):
    files = os.listdir(path)
    file_names = [f.split(".")[0] for f in files if f.endswith(".json")]
    return file_names


class PipelineApi:
    def __init__(self, paths):
        self.PATHS = paths
        self.PIPELINES = paths.pipelines

    def save_pipeline(self, config):
        pipeline_id = config["id"]
        """Save a pipeline configuration as a JSON file in the storage/pipelines directory."""
        file_path = os.path.join(self.PIPELINES, f"{pipeline_id}.json")
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)  # Save with indentation for readability
        return {"message": f"Pipeline {pipeline_id} saved."}

    def load_pipeline(self, pipeline_id):
        """Load a pipeline configuration from a JSON file in the storage/pipelines directory."""
        file_path = os.path.join(self.PIPELINES, f"{pipeline_id}.json")
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"Pipeline {pipeline_id} not found."}

        with open(file_path, 'r') as file:
            config = json.load(file)
        return config

    def list_pipelines(self):
        """List all saved pipeline configurations by reading filenames in storage/pipelines."""
        pipeline_ids = list_jsons(self.PIPELINES)
        pipelines = [self.load_pipeline(pid) for pid in pipeline_ids]
        return pipelines


class StepsApi:

    def __init__(self, paths):
        self.PATHS = paths
        self.STEPS = paths.steps
        self.step_parser = StepBlueprintParser(
            Register.ParamTypeParser, Register.ParamPickerParser, Register.OperationMapper)
        self._cache = {}
        self.reload_from_storage()

    def reload_from_storage(self):
        self.load_all(use_cache=False)

    def list_ids(self):
        step_ids = list_jsons(self.STEPS)
        return step_ids

    def load_step(self, step_id: str, use_cache=True):
        if use_cache and step_id in self._cache:
            return self._cache[step_id]

        file_path = os.path.join(self.STEPS, f"{step_id}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Step {step_id} does not exist.")
        with open(file_path, 'r') as file:
            data = json.load(file)
        step = self.step_parser(data)
        self._cache[step_id] = step
        return step

    def load_all(self, use_cache=True):
        return [self.load_step(sId, use_cache) for sId in self.list_ids()]


class StorageApi:

    def __init__(self):
        self.PATHS = Paths()
        self.PIPELINES = PipelineApi(self.PATHS)
        self.STEPS = StepsApi(self.PATHS)

    def load_pipeline(self, *args, **kwargs):
        return self.PIPELINES.load_pipeline(*args, **kwargs)
