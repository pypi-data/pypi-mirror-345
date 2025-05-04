import requests
from malama.fileParse.exceptions import InvalidModelError
from .base import LLMBase

class CohereLLM(LLMBase):
    def __init__(self, api_key=None, model=None):
        super().__init__(api_key, model)
        self.api_url = "https://api.cohere.ai/v1/chat"
        self.models_url = "https://api.cohere.ai/v1/models"
        self.model = model
        self._validate_model_name()

    def _validate_model_name(self):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(self.models_url, headers=headers)
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch model list: {str(e)}")

        if response.status_code != 200:
            raise Exception(f"Error fetching models: {response.status_code} - {response.text}")

        models = response.json().get("models", [])
        model_ids = [m.get("name") for m in models]

        if self.model not in model_ids:
            raise InvalidModelError(
                f"The model '{self.model}' is not available. Available models: {model_ids}"
            )

    def _ask_with_model(self, context, question):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"""Context from file:\n{context}\n\nUser Question: {question}"""

        data = {
            "model": self.model,
            "message": prompt,
            "temperature": 0.7,
            "p": 1.0,
            "stream": False
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["text"].strip()
