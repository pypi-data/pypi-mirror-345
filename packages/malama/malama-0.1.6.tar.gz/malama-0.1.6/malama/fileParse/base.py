from abc import ABC, abstractmethod
from .context import PDFContext
from .exceptions import MissingAPIKeyError, MissingModelError, NoFileFound, EmptyQueryError

class LLMBase(ABC):
    def __init__(self, api_key, model):
        self.model = model
        self.api_key = api_key
        self._validate()

    def _validate(self):
        if not self.api_key:
            raise MissingAPIKeyError("No api key is provided. Api key is required.")
        
        if not self.model:
            raise MissingModelError("No model name provided. Model name is required.")
        
        if self.model is not None and not isinstance(self.model, str):
            raise ValueError("Model name should be string.")
        
    def ask(self, question):
        if not PDFContext.is_loaded():
            raise NoFileFound("No file loaded yet.")
        if not question.strip():
            raise EmptyQueryError("The question is empty.")

        return self._ask_with_model(PDFContext.get_text(), question)

    @abstractmethod
    def _ask_with_model(self, context, question):
        pass
