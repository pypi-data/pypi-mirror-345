import anthropic
from malama.fileParse.exceptions import InvalidModelError
from .base import LLMBase

class ClaudeLLM(LLMBase):
    def __init__(self, api_key=None, model=None):
        super().__init__(api_key, model)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self._validate_model_name()

    def _validate_model_name(self):
        try:
            models_response = self.client.models.list()
        except Exception as e:
            raise Exception(f"Failed to fetch Claude model list: {str(e)}")

        available_models = [model.id for model in models_response.data]

        if self.model not in available_models:
            raise InvalidModelError(
                f"The model '{self.model}' is not available. Available models: {available_models}"
            )

    def _ask_with_model(self, context, question):
        prompt = f"""Context from file:\n{context}\n\nUser Question: {question}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text.strip()
