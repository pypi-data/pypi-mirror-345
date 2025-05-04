import requests
from malama.fileParse.exceptions import InvalidModelError
from .base import LLMBase

class TogetherAILLM(LLMBase):
    def __init__(self, api_key=None, model=None):
        super().__init__(api_key, model)
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.together.ai/v1/chat/completions"
        self.models_url = "https://api.together.ai/v1/models"
        self._validate_model_name()

    def _validate_model_name(self):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(self.models_url, headers=headers)
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch model list: {str(e)}")

        if response.status_code != 200:
            raise Exception(f"Error fetching models: {response.status_code} - {response.text}")

        models = response.json()
        model_ids = [m.get("id") for m in models]

        if self.model not in model_ids:
            raise InvalidModelError(f"The model '{self.model}' is not available. Available models: {model_ids}")

    def _ask_with_model(self, context, question):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        prompt = f"""Context from file:\n{context}\n\nUser Question: {question}"""

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You're a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
