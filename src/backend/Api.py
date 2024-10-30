import json
import os


class Api:
    def __init__(self):
        # Define the storage directory for pipelines
        self.storage_path = os.path.join(os.path.dirname(__file__), 'storage', 'pipelines')
        os.makedirs(self.storage_path, exist_ok=True)  # Create directory if it doesn’t exist

    def save_pipeline(self, pipeline_id, config):
        """Save a pipeline configuration as a JSON file in the storage/pipelines directory."""
        file_path = os.path.join(self.storage_path, f"{pipeline_id}.json")
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)  # Save with indentation for readability
        return {"status": "success", "message": f"Pipeline {pipeline_id} saved."}

    def load_pipeline(self, pipeline_id):
        """Load a pipeline configuration from a JSON file in the storage/pipelines directory."""
        file_path = os.path.join(self.storage_path, f"{pipeline_id}.json")
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"Pipeline {pipeline_id} not found."}

        with open(file_path, 'r') as file:
            config = json.load(file)
        return {"status": "success", "data": config}

    def list_pipelines(self):
        """List all saved pipeline configurations by reading filenames in storage/pipelines."""
        files = os.listdir(self.storage_path)
        pipeline_ids = [f.split(".")[0] for f in files if f.endswith(".json")]
        pipelines = [self.load_pipeline(pid) for pid in pipeline_ids]
        return {"status": "success", "data": pipelines}
