import os
import sys

from backend.generaltypes import FrontendNotifier
from backend.transferObjects.eventTransferObjects import LogLevels




def load_spacy_model_on_demand(model_name: str, notifier: FrontendNotifier):
    """
    Checks if the specified spaCy model is available. If not, downloads it using spacy cli and pip.

    Caution:
        !!! This function uses the spacy.cli.download function, which requires pip to be installed. !!!


    """

    from backend.storage.storageApi import Paths
    cache_dir = os.path.join(Paths().cache, "spacy", "models")
    os.makedirs(cache_dir, exist_ok=True)

    import spacy

    try:
        notifier.log(f"Checking availability of spaCy model '{model_name}'...", LogLevels.INFO)
        nlp = spacy.load(os.path.join(cache_dir, model_name))
        notifier.log(f"spaCy model '{model_name}' is already installed.", LogLevels.INFO)
    except OSError:
        try:
            notifier.log(f"spaCy model '{model_name}' not found. Downloading...", LogLevels.WARN)
            notifier.log(f"This may take a moment.", LogLevels.WARN)
            spacy.cli.download(model_name)
            notifier.log(f"Download complete. Now loading '{model_name}'...", LogLevels.INFO)
            nlp = spacy.load(model_name)
            nlp.to_disk(os.path.join(cache_dir, model_name))
        except OSError:
            notifier.log(f"Failed to download spaCy model '{model_name}'.", LogLevels.ERROR)
            notifier.log(f"You do not seem to have the python package installer (pip) installed. If you want to download languages packs dynamically install 'pip' .", LogLevels.ERROR)
            notifier.log(f"Otherwise, in order to use '{model_name}' please install the required language pack manually into cache/spacy/models.", LogLevels.INFO)
            notifier.log(f"Download the model from https://spacy.io/models/", LogLevels.INFO)
            notifier.log(f"Using standard language pack for english instead (en_core_web_sm): ...", LogLevels.WARN)
            nlp = spacy.load("en_core_web_sm")
    return nlp
