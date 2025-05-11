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
    os.makedirs(path, exist_ok=True)
    return path


def _set_hf_cache():
    cache_root = _get_or_create_internal()
    os.environ["HF_HOME"] = cache_root
    os.environ["HF_DATASETS_CACHE"] = os.path.join(cache_root, "datasets")
    os.environ["TRANSFORMERS_CACHE"] = os.path.join(cache_root, "transformers")


def ensure_transformer(model_name: str):
    from transformers import AutoTokenizer, AutoModel
    from huggingface_hub import snapshot_download

    _set_hf_cache()
    cache_dir = _get_or_create_internal()

    try:
        # Check if model exists locally
        snapshot_download(
            model_name,
            cache_dir=cache_dir,
            local_files_only=True
        )
    except FileNotFoundError:
        # Download with proper structure
        snapshot_download(
            model_name,
            cache_dir=cache_dir,
            allow_patterns=["*.json", "*.model", "*.bin", "*.safetensors"]
        )

    # Now load normally
    AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    AutoModel.from_pretrained(model_name, cache_dir=cache_dir)


def load_transformer(model_name: str):
    """
    Ensure the model is cached, then load and return (tokenizer, model)
    strictly from disk (no network).
    """
    from transformers import AutoTokenizer, AutoModel

    _set_hf_cache()
    cache_dir = _get_or_create_internal()

    # First, ensure the files are present
    ensure_transformer(model_name)

    # Then load offline
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        cache_dir=cache_dir,
        local_files_only=True
    )
    model = AutoModel.from_pretrained(
        model_name,
        cache_dir=cache_dir,
        local_files_only=True
    )
    return tokenizer, model


def load_pipeline(task: str, model_name: str):
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

    _set_hf_cache()
    cache_dir = _get_or_create_internal()

    # 1) Make sure the files are on disk (this will fetch if missing)
    try:
        AutoTokenizer.from_pretrained(model_name, local_files_only=True, cache_dir=cache_dir)
        AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True, cache_dir=cache_dir)
    except OSError:
        AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=cache_dir)

    # 2) Load strictly offline
    tok = AutoTokenizer.from_pretrained(model_name, local_files_only=True, cache_dir=cache_dir)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True, cache_dir=cache_dir)

    # 3) Build a pipeline with preloaded objects
    return pipeline(task, model=mdl, tokenizer=tok)


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
