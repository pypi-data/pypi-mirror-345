from langchain_openai import OpenAI,AzureOpenAI
from typing import Optional, List
import os
__all__ = ["OPENAI",'AzureOpenAI']

class OPENAI(OpenAI):
    """
    Custom OpenAI Text Completion Model Wrapper using LangChain's OpenAI backend.

    This class wraps LangChain's OpenAI LLM with convenient defaults 
    and parameter customization for OpenAI's text completion models 
    like `text-davinci-003`.

    Environment Variables:
    ----------------------
    - OPENAI_API_KEY : Your OpenAI API key (required if api_key not passed).

    Example:
    --------
    >>> llm = OPENAI(model_name="text-davinci-003")
    >>> response = llm.invoke("Write a poem about the ocean.")
    >>> print(response)

    """

    def __init__(
        self,
        model_name: str = 'text-davinci-003',
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        best_of: int = 1,
        n: int = 1,
        logit_bias: dict = None,
        stop: Optional[List[str]] = None,
        streaming: bool = False,
        api_key: str = None,
        **kwargs
    ):
        """
        Initialize the OPENAI text completion model.

        Parameters:
        -----------
        model_name : str
            OpenAI model name to use (default is 'text-davinci-003').

        temperature : float
            Sampling temperature (default is 0.7).

        max_tokens : int
            Maximum tokens to generate (default is 512).

        top_p : float
            Nucleus sampling probability (default is 1.0).

        frequency_penalty : float
            Penalty for repeated tokens (default is 0.0).

        presence_penalty : float
            Penalty for new topic encouragement (default is 0.0).

        best_of : int
            Number of best completions to return (default is 1).

        n : int
            Number of completions to generate per prompt (default is 1).

        logit_bias : dict
            Bias specific tokens during generation (default is empty dict).

        stop : Optional[List[str]]
            Stop sequences where the model should stop (optional).

        streaming : bool
            Enable streaming responses (default is False).

        api_key : str
            OpenAI API key. Falls back to OPENAI_API_KEY env variable.

        **kwargs : dict
            Additional keyword arguments supported by LangChain's OpenAI model.
        """
        super().__init__(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            best_of=best_of,
            n=n,
            logit_bias=logit_bias or {},
            stop=stop,
            streaming=streaming,
            api_key=api_key,  
            **kwargs
        )








