import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock the webview module before any tests or their dependencies try to import it
sys.modules['webview'] = MagicMock()

sys.modules['backend.operations.operation_utils'] = MagicMock()

# Mock bertopic and its submodules
bertopic_mock = MagicMock()
bertopic_mock.vectorizers = MagicMock()
# Correctly mock the BERTopic class and its instance's fit and transform methods
bertopic_mock.BERTopic = MagicMock()
bertopic_mock.BERTopic.return_value.fit.return_value = None # fit doesn't return anything
bertopic_mock.BERTopic.return_value.transform.return_value = ([0], [0.5]) # transform returns two values, each with a single element

topic_freq_mock = MagicMock()
topic_freq_mock.__len__.return_value = 1 # Return a mock with length 1
bertopic_mock.BERTopic.return_value.get_topic_freq.return_value = topic_freq_mock

# Make visualization methods return a MagicMock with a to_json method
plotly_viz_mock = MagicMock()
plotly_viz_mock.to_json.return_value = {"data": [], "layout": {}}

bertopic_mock.BERTopic.return_value.visualize_barchart.return_value = plotly_viz_mock
bertopic_mock.BERTopic.return_value.visualize_hierarchy.return_value = plotly_viz_mock
bertopic_mock.BERTopic.return_value.visualize_heatmap.return_value = plotly_viz_mock

sys.modules['bertopic'] = bertopic_mock
sys.modules['bertopic.vectorizers'] = MagicMock()

# Mock sklearn and its submodules
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.cluster'] = MagicMock()
sys.modules['sklearn.feature_extraction'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'] = MagicMock()

# Mock hdbscan
sys.modules['hdbscan'] = MagicMock()

# Mock spacy and its submodules
spacy_mock = MagicMock()

# Define some mock stopwords for testing
mock_stop_words = {"is", "a", "for", "it", "this", "another"}



class MockDoc:
    def __init__(self, text):
        self.text = text # Add text attribute
        self.tokens = []
        for word in text.split():
            token_mock = MagicMock()
            token_mock.text = word
            token_mock.is_stop = (word.lower() in mock_stop_words)
            token_mock.is_alpha = word.isalpha()
            token_mock.lemma_ = word.lower().replace("testing", "test").replace(".", "")
            self.tokens.append(token_mock)

    def __iter__(self):
        return iter(self.tokens)

def mock_spacy_load(*args, **kwargs):
    nlp_mock = MagicMock()
    def mock_nlp_call(text):
        return MockDoc(text)
    nlp_mock.side_effect = mock_nlp_call
    return nlp_mock

spacy_mock.load.side_effect = mock_spacy_load
sys.modules['spacy'] = spacy_mock
sys.modules['spacy.lang'] = MagicMock()
sys.modules['spacy.lang.en'] = MagicMock()
sys.modules['spacy.lang.en.stop_words'] = MagicMock()
sys.modules['spacy.lang.en.stop_words'].STOP_WORDS = mock_stop_words # Provide mock STOP_WORDS

def mock_load_pipeline(task, model_name):
    if task == "sentiment-analysis":
        def sentiment_pipeline_callable(text, padding, truncation):
            if "great" in text:
                return [{'label': 'POSITIVE', 'score': 0.999}]
            elif "hate" in text:
                return [{'label': 'NEGATIVE', 'score': 0.998}]
            else:
                return [{'label': 'NEUTRAL', 'score': 0.5}]
        return sentiment_pipeline_callable
    return MagicMock() # Default return for other tasks

sys.modules['backend.operations.operation_utils'].load_pipeline.side_effect = mock_load_pipeline

def mock_load_transformer(model_name):
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()

    # Mock tokenizer behavior
    def mock_tokenizer_call(text, return_tensors, padding, truncation, max_length):
        # Return a mock object that has a .to() method
        mock_inputs = MagicMock()
        mock_inputs.to.return_value = mock_inputs # Chain .to() calls
        mock_inputs.input_ids = MagicMock()
        mock_inputs.attention_mask = MagicMock()
        mock_inputs.attention_mask.to.return_value = MagicMock()
        return mock_inputs
    mock_tokenizer.side_effect = mock_tokenizer_call

    # Mock model behavior
    def mock_model_call(**kwargs):
        mock_outputs = MagicMock()
        mock_outputs.last_hidden_state = MagicMock()
        return mock_outputs
    mock_model.side_effect = mock_model_call

    # Mock compute_embedding and cosine_similarity
    def mock_compute_embedding(text):
        mock_embedding = MagicMock()
        mock_embedding.text = text # Add text attribute
        mock_embedding.dim = 1 # Add a dummy dim attribute
        mock_embedding.item.return_value = 0.0 # Add a dummy item method
        return mock_embedding

    def mock_cosine_similarity(emb1, emb2, dim):
        # Return a dummy similarity score based on input text
        # Access the original text from the mocked embeddings
        text1 = emb1._mock_name.split('text=')[1].split(')')[0] if 'text=' in emb1._mock_name else ""
        text2 = emb2._mock_name.split('text=')[1].split(')')[0] if 'text=' in emb2._mock_name else ""

        if "cat" in text1 and "cat" in text2:
            return MagicMock(item=lambda: 0.9) # High similarity
        elif "love" in text1 and "hate" in text2:
            return MagicMock(item=lambda: 0.1) # Low similarity
        return MagicMock(item=lambda: 0.5) # Default

    # Patch the actual functions within the module
    sys.modules['backend.operations.TextSimilarityOperation'].TextSimilarityAnalysisOperation.compute_embedding = mock_compute_embedding
    sys.modules['backend.operations.TextSimilarityOperation'].TextSimilarityAnalysisOperation.compute_similarity = mock_cosine_similarity

    return mock_tokenizer, mock_model

sys.modules['backend.operations.operation_utils'].load_transformer.side_effect = mock_load_transformer
