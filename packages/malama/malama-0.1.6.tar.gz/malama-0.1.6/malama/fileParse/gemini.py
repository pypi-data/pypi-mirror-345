import google.generativeai as genai
from .base import LLMBase
                                                                                                
class GeminiLLM(LLMBase):
    def __init__(self, api_key=None, model=None):
        super().__init__(api_key, model)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def _ask_with_model(self, context, question):
        prompt = f"""Context from File:\n{context}\n\nUser Question: {question}"""
        response = self.model.generate_content(prompt)
        return response.text.strip()

    