import json
import os

import webview

from backend.events.backendEventApi import BackendEventApi
from backend.storage.storageApi import StorageApi


class Api:
    STORAGE = StorageApi()

    def __init__(self):
        self._backendEventApi = BackendEventApi()

