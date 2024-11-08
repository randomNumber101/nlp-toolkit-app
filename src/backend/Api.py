import json
import os

from backend.storage.storageApi import StorageApi


class Api:

    STORAGE = StorageApi()

    def __init__(self):
        # Define the storage directory for pipelines
        self.storage_path = os.path.join(os.path.dirname(__file__), 'storage', 'pipelines')
        os.makedirs(self.storage_path, exist_ok=True)  # Create directory if it doesn’t exist

