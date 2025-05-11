import os
import sys

from backend.transferObjects.eventTransferObjects import LogLevels
from backend.types.frontendNotifier import FrontendNotifier

from backend.storage.paths import PATHS


def load_spacy_model_on_demand(model_name: str, notifier: FrontendNotifier):
    """
    Checks if the specified spaCy model is available. If not, downloads it using spacy cli and pip.

    Caution:
        !!! This function uses the spacy.cli.download function, which requires pip to be installed. !!!


    """

    cache_dir = os.path.join(PATHS.cache, "spacy", "models")
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
            notifier.log(
                f"You do not seem to have the python package installer (pip) installed. If you want to download languages packs dynamically install 'pip' .",
                LogLevels.ERROR)
            notifier.log(
                f"Otherwise, in order to use '{model_name}' please install the required language pack manually into cache/spacy/models.",
                LogLevels.INFO)
            notifier.log(f"Download the model from https://spacy.io/models/", LogLevels.INFO)
            notifier.log(f"Using standard language pack for english instead (en_core_web_sm): ...", LogLevels.WARN)
            nlp = spacy.load("en_core_web_sm")
    return nlp


def _get_or_create_internal():
    path = os.path.join(PATHS.cache, "models")
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def _set_hf_cache():
    """Point all HF downloads to internal_storage."""
    internal_storage = str(_get_or_create_internal)
    os.environ.setdefault("TRANSFORMERS_CACHE", internal_storage)
    os.environ.setdefault("HF_HOME", internal_storage)



def ensure_transformer(model_name: str):
    from transformers import AutoTokenizer, AutoModel
    internal_storage = _get_or_create_internal()

    """Download tokenizer + model if missing, then return local paths."""
    _set_hf_cache()

    # tokenizer
    try:
        AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    except OSError:
        AutoTokenizer.from_pretrained(model_name, cache_dir=internal_storage)
    # model
    try:
        AutoModel.from_pretrained(model_name, local_files_only=True)
    except OSError:
        AutoModel.from_pretrained(model_name, cache_dir=internal_storage)


def load_transformer(model_name: str):
    from transformers import AutoTokenizer, AutoModel
    internal_storage = _get_or_create_internal()

    """Ensure download and return (tokenizer, model) loaded from internal_storage."""
    ensure_transformer(model_name)
    tok = AutoTokenizer.from_pretrained(model_name,
                                        cache_dir=internal_storage,
                                        local_files_only=True)
    mdl = AutoModel.from_pretrained(model_name,
                                    cache_dir=internal_storage,
                                    local_files_only=True)
    return tok, mdl


def load_pipeline(task: str, model_name: str):
    from transformers import pipeline
    internal_storage = _get_or_create_internal()

    """Ensure pipeline model is cached, then load it offline."""
    _set_hf_cache()
    try:
        # fast path if already cached
        return pipeline(task, model=model_name, local_files_only=True)
    except OSError:
        # initial download
        return pipeline(task, model=model_name, cache_dir=internal_storage)


def load_sentence_transformer(model_name: str):
    from sentence_transformers import SentenceTransformer
    internal_storage = _get_or_create_internal()

    """Ensure sentence-transformers model is cached, then load it offline."""
    _set_hf_cache()
    try:
        return SentenceTransformer(model_name,
                                   cache_folder=internal_storage,
                                   local_files_only=True)
    except Exception:
        # initial download
        return SentenceTransformer(model_name,
                                   cache_folder=internal_storage)
