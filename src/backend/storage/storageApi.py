import json

from typing import Optional

from backend.storage.parsing import StepBlueprintParser, PipelineParser
from backend.register import Register
from backend.transferObjects.pipelineTransferObjects import convert_pipeline_to_transfer, \
    convert_step_blueprint_to_transfer

from backend.types.blueprint import StepBlueprint
from backend.types.pipeline import Pipeline

from backend.storage.paths import PATHS

import os



def list_jsons(path):
    files = os.listdir(path)
    file_names = [f.split(".")[0] for f in files if f.endswith(".json")]
    return file_names


class PipelineApi:
    def __init__(self, paths):
        self.PATHS = paths
        self.PIPELINES = paths.pipelines

    def delete_pipeline(self, pipeline_id):
        file_path = os.path.join(self.PIPELINES, f"{pipeline_id}.json")
        if not os.path.exists(file_path):
            return False
        os.remove(file_path)
        return True

    def save_pipeline(self, pipeline):
        jsonObj = PipelineParser.to_json(pipeline)
        file_path = os.path.join(self.PIPELINES, f"{pipeline.id}.json")
        with open(file_path, 'w') as file:
            json.dump(jsonObj, file, indent=4)

    def load_pipeline(self, pipeline_id) -> Pipeline:
        """Load a pipeline configuration from a JSON file in the storage/pipelines directory."""
        file_path = os.path.join(self.PIPELINES, f"{pipeline_id}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No pipeline with if {pipeline_id} found")

        with open(file_path, 'r') as file:
            config = json.load(file)
            pipeline = PipelineParser.from_json(config)
        return pipeline

    def load_all(self) -> list[Pipeline]:
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

    def list_ids(self) -> list[str]:
        step_ids = list_jsons(self.STEPS)
        return step_ids

    def load_step(self, step_id: str, use_cache=True) -> StepBlueprint:
        if use_cache and step_id in self._cache:
            return self._cache[step_id]

        file_path = os.path.join(self.STEPS, f"{step_id}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Step {step_id} does not exist.")
        with open(file_path, 'r') as file:
            print("Loading step", step_id)
            data = json.load(file)
        step = self.step_parser(data)
        if step.information is None or step.information == "<html>":
            step.information = self.load_description_html(step_id)

        self._cache[step_id] = step
        return step

    def load_description_html(self, step_id: str) -> Optional[str]:
        file_path = os.path.join(self.STEPS, "descriptions", f"{step_id}.html")
        if not os.path.exists(file_path):
            print(f"Description file not found: {file_path}")  # Debug log
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                print(f"Loaded HTML content for {step_id}: {content[:100]}...")  # Debug log
                return content
        except UnicodeDecodeError as e:
            print(f"Failed to read {file_path} with UTF-8 encoding: {e}")
            return None

    def load_all(self, use_cache=True) -> list[StepBlueprint]:
        return [self.load_step(sId, use_cache) for sId in self.list_ids()]


class StorageApi:

    def __init__(self):
        self.PATHS = PATHS
        self.PIPELINES = PipelineApi(self.PATHS)
        self.STEPS = StepsApi(self.PATHS)

    def load_pipeline(self, pipeline_id):
        pipeline = self.PIPELINES.load_pipeline(pipeline_id)
        return convert_pipeline_to_transfer(pipeline).to_dict()

    def load_all_pipelines(self):
        pipelines = self.PIPELINES.load_all()
        return [convert_pipeline_to_transfer(p).to_dict() for p in pipelines]

    def save_pipeline(self, pipelineObj):
        # Deserialize and serialize to ensure type compatibility
        pipeline = PipelineParser.from_json(pipelineObj)
        self.PIPELINES.save_pipeline(pipeline)
        return True

    def delete_pipeline(self, pipeline_id):
        return self.PIPELINES.delete_pipeline(pipeline_id)

    def load_step(self, step_id):
        stepBP = self.STEPS.load_step(step_id)
        return convert_step_blueprint_to_transfer(stepBP).to_dict()

    def load_all_steps(self):
        stepBPs = self.STEPS.load_all()
        return [convert_step_blueprint_to_transfer(stepBP).to_dict() for stepBP in stepBPs]
