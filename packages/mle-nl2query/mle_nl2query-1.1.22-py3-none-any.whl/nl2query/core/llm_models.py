
# nl2query/core/models.py

import os

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI


class LLMModelLoader:
    """
    A generic loader for language models using LangChain.

    Parameters:
        model_type (str): Type of the model ("openai", "gemini", "claude" or "anthropic").  
                          If not provided, will be loaded from the `MODEL_TYPE` environment variable (default: "openai").
        model_name (str): The name or id of the model. If not provided, will be loaded from the `MODEL_NAME` environment variable.
        temperature (float): The sampling temperature. If not provided, will be loaded from the `MODEL_TEMPERATURE` environment variable.
        **kwargs: Any additional parameters that the model supports.
    """

    def __init__(self, model_type: str = None, model_name: str = None, temperature: float = None, **kwargs):
        self.model_type = (model_type or os.environ.get("MODEL_TYPE", "openai")).lower()
        self.model_name = model_name or os.environ.get("MODEL_NAME", "text-davinci-003")
        # Convert the temperature to float if it comes from environment
        self.temperature = temperature if temperature is not None else float(os.environ.get("MODEL_TEMPERATURE", 0.7))
        self.kwargs = kwargs

    def load_model(self):
        """
        Instantiates and returns the LLM based on the specified model_type.
        """
        if self.model_type == "openai":
            return ChatOpenAI(model_name=self.model_name, temperature=self.temperature, **self.kwargs)
        elif self.model_type in ["claude", "anthropic"]:
            # Note: The Anthropic class might expect the model name as "model" instead of "model_name".
            return ChatAnthropic(model=self.model_name, temperature=self.temperature, **self.kwargs)
        elif self.model_type == "gemini":
            return ChatVertexAI(model=self.model_name, temperature=self.temperature, **self.kwargs)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

def get_llm(model_type: str = None, model_name: str = None, temperature: float = None, **kwargs):
    """
    Convenience function to load and return an LLM instance.

    Usage:
        llm = get_llm(model_type="openai", model_name="gpt-3.5-turbo", temperature=0.5)
    """
    loader = LLMModelLoader(model_type, model_name, temperature, **kwargs)
    return loader.load_model()