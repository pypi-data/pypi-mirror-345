from abc import ABC, abstractmethod
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch


class MyReranker(ABC):

    def __init__(self, model_name: str, verbose=False):
        self.verbose = verbose
        self.model_name = model_name

    @abstractmethod
    def rerank(self, query:str, documents: list):
        pass


class JinaRerankerV2(MyReranker):
    def __init__(self, model_name: str = "jinaai/jina-reranker-v2-base-multilingual", verbose=False):
        super().__init__(model_name, verbose)

        # Load the Jina Reranker v2 model and tokenizer
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            torch_dtype="auto",
            trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def rerank(self, query: str, documents: list):
        # Create sentence pairs for the model
        sentence_pairs = [[query, doc] for doc in documents]

        # Tokenize the input
        inputs = self.tokenizer(sentence_pairs, padding=True, truncation=True, return_tensors="pt", max_length=1024)

        # Get the model's predictions
        with torch.no_grad():
            scores = self.model(**inputs).logits

        # Return the scores for each document
        return scores.float().numpy().tolist()

