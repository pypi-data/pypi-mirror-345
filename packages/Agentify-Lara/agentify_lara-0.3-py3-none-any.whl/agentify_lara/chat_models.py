__all__ = ["CHATGROQ",'CHATOPENROUTER','AzureChatOpenAI','ChatAnthropic'
           ,'init_chat_model','ChatGoogleGenerativeAI']

from typing import Optional, List, Dict, Any

# Inherit from langchain_groq.ChatGroq
from langchain_groq import ChatGroq
from langchain.chat_models import ChatOpenAI
import os
from langchain.chat_models import AzureChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.chat_models.anthropic import ChatAnthropic
from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI
class CHATGROQ(ChatGroq):
    """
    Custom Groq Chat Model using LangChain's ChatGroq backend.

    This class provides a convenient wrapper around LangChain's ChatGroq
    with default parameters and environment-based API key handling.

    Environment Variables:
    ----------------------
    - GROQ_API_KEY : Your Groq API key (required if api_key not passed).

    Example:
    --------
    >>> llm = CHATGROQ(model_name="llama3-8b-8192")
    >>> response = llm.invoke("Tell me a joke!")
    >>> print(response)

    """

    def __init__(
        self,
        model_name: str = "llama-3.1-8b-instant",
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 1.0,
        stop: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        streaming: bool = False,
        **kwargs: Any
    ):
        """
        Initialize the CHATGROQ model.

        Parameters:
        -----------
        model_name : str
            Model name to use (default is "llama-3.1-8b-instant").

        temperature : float
            Sampling temperature (default is 0.7).

        max_tokens : int
            Maximum tokens to generate (default is 512).

        top_p : float
            Nucleus sampling probability (default is 1.0).

        stop : Optional[List[str]]
            Stop sequences where the model should stop (optional).

        api_key : Optional[str]
            Groq API key. Falls back to GROQ_API_KEY env variable.

        streaming : bool
            Enable streaming responses (default is False).

        **kwargs : dict
            Additional keyword arguments supported by LangChain's ChatGroq.
        """
        super().__init__(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop,
            api_key=api_key,
            streaming=streaming,
            **kwargs
        )
#############################################################################################################################
class CHATOPENROUTER(ChatOpenAI):
    """
    Custom OpenRouter Chat Model using LangChain's ChatOpenAI backend.

    This class routes chat completions through OpenRouter's unified API
    and simplifies environment variable handling for authentication.

    Environment Variables:
    ----------------------
    - OPENROUTER_API_KEY : Your OpenRouter API key (required if api_key not passed)
    - OPENAI_API_KEY     : Optional fallback API key (used if OPENROUTER_API_KEY not set)

    Note:
    -----
    This class automatically sets the OpenAI API base to OpenRouter's endpoint.

    Example:
    --------
    >>> llm = CHATOPENROUTER(model_name="mistralai/mistral-7b-instruct")
    >>> response = llm.invoke("Hello, OpenRouter!")
    >>> print(response)

    """

    def __init__(
        self,
        model_name: str = 'mistralai/mistral-7b-instruct',
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 1.0,
        n: int = 1,
        stop: Optional[List[str]] = None,
        streaming: bool = False,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the CHATOPENROUTER model.

        Parameters:
        -----------
        model_name : str
            Model name to use (e.g., 'mistralai/mistral-7b-instruct').

        temperature : float
            Sampling temperature (default is 0.7).

        max_tokens : int
            Maximum tokens to generate (default is 512).

        top_p : float
            Nucleus sampling probability (default is 1.0).

        n : int
            Number of completions to generate (default is 1).

        stop : Optional[List[str]]
            Stop sequences where the model should stop (optional).

        streaming : bool
            Enable streaming responses (default is False).

        api_key : Optional[str]
            OpenRouter API key. Falls back to OPENROUTER_API_KEY env variable.

        **kwargs : dict
            Additional keyword arguments supported by LangChain's ChatOpenAI.

        Raises:
        -------
        Exception:
            If the required API key environment variable is missing.
        """

        # 🌐 Set base URL before super init
        os.environ['OPENAI_API_BASE'] = "https://openrouter.ai/api/v1"

        # 🔒 Resolve API Key
        resolved_api_key = api_key or os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
        if not resolved_api_key:
            raise Exception('OPENROUTER_API_KEY not found. Please set it in your environment variables.')

        # ✅ Call parent init (Pydantic safe)
        super().__init__(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            n=n,
            stop=stop,
            streaming=streaming,
            api_key=resolved_api_key,
            **kwargs
        )
