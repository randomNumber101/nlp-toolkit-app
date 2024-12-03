from backend.run.backendEventApi import BackendEventApi
from backend.run.RunApi import RunApi
from backend.storage.storageApi import StorageApi


class Api:

    def __init__(self):
        self._backendEventApi = BackendEventApi()
        self.STORAGE = StorageApi()
        self.RUNS = RunApi(self.STORAGE, self._backendEventApi)


