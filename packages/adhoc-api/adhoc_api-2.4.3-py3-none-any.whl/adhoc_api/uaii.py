"""Universal AI Interface (UAII) for OpenAI GPT-4 and (eventually) other AI models."""

import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Literal, Generator
from openai import OpenAI
from google import genai
from google.genai import types as genai_types
from typing import overload, TypedDict, Literal
from typing_extensions import Annotated, NotRequired
from tiktoken import get_encoding

from .utils import Logger, SimpleLogger

import pdb



"""
TODO: long term want this to be more flexible/generic
mixin classes to cover different features that LLMs may have (text, images, audio, video)
class GPT4o: ...
class GPT4Vision: ...
use __new__ to look at the model type and return the appropriate class for type hints

class OpenAIAgent:
    @overload
    def __new__(cls, model: Literal['gpt-4o', 'gpt-4o-mini'], timeout=None) -> GPT4o: ...
    @overload
    def __new__(cls, model: Literal['gpt-4v', 'gpt-4v-mini'], timeout=None) -> GPT4Vision: ...
    def __new__(cls, model: OpenAIModel, timeout=None):
        if model in ['gpt-4o', 'gpt-4o-mini']:
            return GPT4o(model, timeout)
        elif model in ['gpt-4v', 'gpt-4v-mini']:
            return GPT4Vision(model, timeout)
        elif:
            ...
"""


class UAII(ABC):
    @abstractmethod
    def multishot(self, messages: list[dict], stream:bool=False, **kwargs) -> Generator[str, None, None]|str: ...
    @abstractmethod
    def oneshot(self, query:str, stream:bool=False, **kwargs) -> Generator[str, None, None]|str: ...
    @abstractmethod
    def message(self, message:str, stream:bool=False, **kwargs) -> Generator[str, None, None]|str: ...
    @abstractmethod
    def push_user_message(self, message:str): ...
    @abstractmethod
    def push_assistant_message(self, message:str): ...
    @abstractmethod
    def clear_messages(self): ...
    @abstractmethod
    def set_system_prompt(self, prompt:str): ...
    @abstractmethod
    def count_tokens(self, message:str) -> int: ...
    @abstractmethod
    def get_context_window_size(self) -> int: ...


################## For now, only OpenAIAgent uses this ##################

class OpenAIRole(str, Enum):
    system = "system"
    assistant = "assistant"
    user = "user"

class OpenAIMessage(dict):
    def __init__(self, role: OpenAIRole, content: str):
        super().__init__(role=role.value, content=content)


OpenAIModel = Literal['gpt-4.1', 'gpt-4o', 'gpt-4o-mini', 'o3-mini', 'o1', 'o1-preview', 'o1-mini', 'gpt-4', 'gpt-4-turbo']
openai_context_sizes: dict[OpenAIModel, int] = {
    'gpt-4.1': 1_047_576,
    'gpt-4o': 128_000,
    'gpt-4o-mini': 128_000,
    'o3-mini': 200_000,
    'o1': 200_000,
    'o1-preview': 128_000,
    'o1-mini': 128_000,
    'gpt-4': 8192,
    'gpt-4-turbo': 128_000,
}

# models that don't support temperature parameter
no_temperature_models: set[OpenAIModel] = {
    'o3-mini',
    'o1',
    'o1-preview',
    'o1-mini',
}

# See: https://github.com/openai/tiktoken/blob/main/tiktoken/model.py
OpenAITokenizer = Literal['o200k_base', 'cl100k_base', 'p50k_base', 'r50k_base', 'gpt2']
openai_tokenizers: dict[OpenAIModel, OpenAITokenizer] = {
    'gpt-4.1': 'o200k_base',
    'gpt-4o': 'o200k_base',
    'gpt-4o-mini': 'o200k_base',
    'o3-mini': 'o200k_base',
    'o1': 'o200k_base',
    'o1-preview': 'o200k_base',
    'o1-mini': 'o200k_base',
    'gpt-4': 'cl100k_base',
    'gpt-4-turbo': 'cl100k_base',
}

class OpenAIAgent(UAII):
    def __init__(self, *, model: OpenAIModel, system_prompt:str|None=None, timeout:float|None=None, logger:Logger=SimpleLogger()):
        self.model = model
        self.timeout = timeout
        self.logger = logger
        self.messages: list[OpenAIMessage] = []
        self.set_system_prompt(system_prompt)
        
    def _chat_gen(self, messages: list[OpenAIMessage], **kwargs) -> Generator[str, None, None]:
        client = OpenAI()
        
        # remove temperature parameter if not supported in model
        temperature_param = {} if self.model in no_temperature_models else {'temperature': 0.0}  
        
        gen = client.chat.completions.create(
            model=self.model,
            messages=[*self.system_prompt, *messages],
            timeout=self.timeout,
            stream=True,
            **temperature_param,
            **kwargs
        )
        chunks: list[str] = []
        for chunk in gen:
            try:
                content = chunk.choices[0].delta.content
                if content:
                    chunks.append(content)
                    yield content
            except:
                pass
    
        # save the agent response to the list of messages
        messages.append(OpenAIMessage(role=OpenAIRole.assistant, content=''.join(chunks)))
        self.messages = messages

    @overload
    def multishot(self, messages: list[OpenAIMessage], stream:Literal[True], **kwargs) -> Generator[str, None, None]: ...
    @overload
    def multishot(self, messages: list[OpenAIMessage], stream:Literal[False]=False, **kwargs) -> str: ...
    def multishot(self, messages: list[OpenAIMessage], stream:bool=False, **kwargs) -> Generator[str, None, None]|str:
        gen = self._chat_gen(messages, **kwargs)
        return gen if stream else ''.join([*gen])
    
    @overload
    def oneshot(self, query:str, stream:Literal[True], **kwargs) -> Generator[str, None, None]: ...
    @overload
    def oneshot(self, query:str, stream:Literal[False]=False, **kwargs) -> str: ...
    def oneshot(self, query:str, stream:bool=False, **kwargs) -> Generator[str, None, None]|str:
        self.clear_messages()
        self.messages.append(OpenAIMessage(role=OpenAIRole.user, content=query))
        return self.multishot(self.messages, stream=stream, **kwargs)
    
    @overload
    def message(self, message:str, stream:Literal[True], **kwargs) -> Generator[str, None, None]: ...
    @overload
    def message(self, message:str, stream:Literal[False]=False, **kwargs) -> str: ...
    def message(self, message:str, stream:bool=False, **kwargs) -> Generator[str, None, None]|str:
        self.messages.append(OpenAIMessage(role=OpenAIRole.user, content=message))
        return self.multishot(self.messages, stream=stream, **kwargs)

    def push_user_message(self, message:str):
        self.messages.append(OpenAIMessage(role=OpenAIRole.user, content=message))

    def push_assistant_message(self, message:str):
        self.messages.append(OpenAIMessage(role=OpenAIRole.assistant, content=message))

    def clear_messages(self):
        self.messages = []
    
    def set_system_prompt(self, system_prompt:str|None):
        self.system_prompt: tuple[()] | tuple[OpenAIMessage] = (
            (OpenAIMessage(role=OpenAIRole.system, content=system_prompt),) 
            if system_prompt else ()
        )


    def count_tokens(self, message: str) -> int:
        tokenizer = openai_tokenizers[self.model]
        encoding = get_encoding(tokenizer)
        return len(encoding.encode(message))

    def get_context_window_size(self) -> int:
        return openai_context_sizes[self.model]



################## For now, keeping gemini agent completely separate ##################

class GeminiRole(str, Enum):
    model = "model"
    user = "user"

class GeminiMessage(dict):
    def __init__(self, role: GeminiRole, content: str):
        super().__init__(role=role.value, parts=[{'text':content}])


GeminiModel = Literal['gemini-1.5-flash-001', 'gemini-1.5-pro-001', 'gemini-2.5-pro-exp-03-25']
gemini_context_sizes: dict[GeminiModel, int] = {
    'gemini-1.5-flash-001': 2_000_000,
    'gemini-1.5-pro-001': 2_000_000,
    'gemini-2.5-pro-exp-03-25': 1_048_576,
}

class GeminiAgent(UAII):
    def __init__(
            self,
            *,
            model: GeminiModel,
            system_prompt:str,
            cache_key:str|None,
            cache_content:str,
            ttl_seconds:int,
            logger:Logger=SimpleLogger()
        ):
        """
        Gemini agent with conversation caching

        Args:
            model (GeminiModel): The model to use for the Gemini API
            cache_key (str): The key used to retrieve the cached API chat
            system_prompt (str): The system prompt for the Gemini API chat
            cache_content (str): The content to cache for the Gemini API chat
            ttl_seconds (int): The time-to-live in seconds for the Gemini API cache.
            logger (Logger, optional): The logger to use for the Gemini API chat. Defaults to SimpleLogger()
        """
        self.model = model
        self.system_prompt = system_prompt
        self.cache_key = cache_key
        self.cache_content = cache_content
        self.cache: genai_types.CachedContent | None = None
        self.ttl_seconds = ttl_seconds
        self.logger = logger

        self.messages: list[GeminiMessage] = []

    def _get_client(self) -> genai.Client:
        return genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
    
    def load_cache(self):
        """Load the cache for the Gemini API chat instance. Raises an exception if unable to make/load the cache."""
        # Don't cache if cache_key is None
        if self.cache_key is None:
            raise ValueError('cache_key is None')

        client = self._get_client()

        # always try to load the cache from the list of live caches so we don't end up with a stale reference
        try:
            # get the most recent cache with the matching display_name
            matching_caches = list(filter(lambda c: c.display_name==self.cache_key, client.caches.list()))
            matching_caches.sort(key=lambda c: c.expire_time, reverse=True)
            self.cache = matching_caches[0]
            self.logger.info({'cache': f'found cached content for "{self.cache_key}"'})
        except Exception as e:
            # skip this for now since we don't know all the possible exceptions that can be raised
            # if 'Invalid CachedContent name' not in str(e):
            #     # re-raise since it's not an expected error
            #     self.logger.error({'cache': f'Unexpected error loading cache "{self.cache_key}": {e}'})
            #     raise
            self.logger.info({'cache': f'No cached content found for "{self.cache_key}". pushing new instance.'})
            # this may raise an exception if the cache content is too small
            self.cache = client.caches.create(
                model=self.model,
                config=genai_types.CreateCachedContentConfig(
                    display_name=self.cache_key,
                    system_instruction=self.system_prompt or None,
                    contents=[GeminiMessage(role=GeminiRole.model, content=self.cache_content)],
                    ttl=f'{self.ttl_seconds}s',  # ttl used to be an int, but now it's a string with units
                )
            )

    def _chat_gen(self, messages: list[GeminiMessage], **kwargs) -> Generator[str, None, None]:
        client = self._get_client()
        try:
            self.load_cache()
            system_messages: tuple[()] = ()
            cache_param = self.cache.name
        except Exception as e:
            if 'Cached content is too small' not in str(e) and 'cache_key is None' not in str(e) and 'not supported for createCachedContent' not in str(e):
                raise
            # if cache is too small or isn't supported, just run the model from scratch without caching
            self.logger.info({'cache': f'{e}. Running model without cache.'})
            system_messages: tuple[GeminiMessage] = (GeminiMessage(role=GeminiRole.model, content=self.cache_content),)
            cache_param = None

        response = client.models.generate_content_stream(
            model=self.model,
            contents=[*system_messages, *messages],
            config = genai_types.GenerateContentConfig(cached_content=cache_param),
            **kwargs
        )
        chunks: list[str] = []
        for chunk in response:
            try:
                content = chunk.text
                if content:
                    chunks.append(content)
                    yield content
            except:
                pass
        
        # save the agent response to the list of messages
        messages.append(GeminiMessage(role=GeminiRole.model, content=''.join(chunks)))
        self.messages = messages

    @overload
    def multishot(self, messages: list[GeminiMessage], stream:Literal[True], **kwargs) -> Generator[str, None, None]: ...
    @overload
    def multishot(self, messages: list[GeminiMessage], stream:Literal[False]=False, **kwargs) -> str: ...
    def multishot(self, messages: list[GeminiMessage], stream:bool=False, **kwargs) -> Generator[str, None, None]|str:
        gen = self._chat_gen(messages, **kwargs)
        return gen if stream else ''.join([*gen])
    
    @overload
    def oneshot(self, query:str, stream:Literal[True], **kwargs) -> Generator[str, None, None]: ...
    @overload
    def oneshot(self, query:str, stream:Literal[False]=False, **kwargs) -> str: ...
    def oneshot(self, query:str, stream:bool=False, **kwargs) -> Generator[str, None, None]|str:
        self.clear_messages()
        self.messages.append(GeminiMessage(role=GeminiRole.user, content=query))
        return self.multishot(self.messages, stream=stream, **kwargs)
    
    @overload
    def message(self, message:str, stream:Literal[True], **kwargs) -> Generator[str, None, None]: ...
    @overload
    def message(self, message:str, stream:Literal[False]=False, **kwargs) -> str: ...
    def message(self, message:str, stream:bool=False, **kwargs) -> Generator[str, None, None]|str:
        self.messages.append(GeminiMessage(role=GeminiRole.user, content=message))
        return self.multishot(self.messages, stream=stream, **kwargs)

    def push_user_message(self, message:str):
        self.messages.append(GeminiMessage(role=GeminiRole.user, content=message))
    
    def push_assistant_message(self, message:str):
        self.messages.append(GeminiMessage(role=GeminiRole.model, content=message))

    def clear_messages(self):
        self.messages = []
    
    def set_system_prompt(self, system_prompt:str, cache_content:str):
        self.system_prompt = system_prompt
        self.cache_content = cache_content
        self.cache = None

    def count_tokens(self, message: str) -> int:
        client = self._get_client()
        res = client.models.count_tokens(model=self.model, contents=message)
        return res.total_tokens

    def get_context_window_size(self) -> int:
        return gemini_context_sizes[self.model]


########################################################################################

from anthropic import Anthropic, NotGiven, NOT_GIVEN
from anthropic.types import TextBlockParam


class ClaudeRole(str, Enum):
    model = "assistant"
    user = "user"

class ClaudeMessage(dict):
    def __init__(self, role: ClaudeRole, text: str):
        super().__init__(role=role.value, content=[{'type': 'text', 'text': text}])


ClaudeModel = Literal['claude-3-7-sonnet-latest', 'claude-3-5-sonnet-latest', 'claude-3-5-haiku-latest']
claude_context_sizes: dict[ClaudeModel, int] = {
    'claude-3-7-sonnet-latest': 200_000,
    'claude-3-5-sonnet-latest': 200_000,
    'claude-3-5-haiku-latest': 200_000,
}


class ClaudeAgent(UAII):
    def __init__(
            self,
            *,
            model: ClaudeModel,
            cache:bool=False,
            system_prompt: str|NotGiven=NOT_GIVEN,
            timeout:float|None=None,
            logger:Logger=SimpleLogger()
        ):
        """
        Create a ClaudeAgent instance

        Args:
            model (ClaudeModel): The model to use for the Claude API
            cache (bool, optional): Whether to cache the system_prompt. Defaults to False.
            system_prompt (str, optional): The system prompt for the Claude API. Defaults to NOT_GIVEN.
            timeout (float, optional): The timeout in seconds for the Claude API. Defaults to None (i.e. no timeout).
            logger (Logger, optional): The logger to use for the Claude API chat. Defaults to SimpleLogger().
        """
        self.model = model
        self.cache = cache
        self.system_prompt = system_prompt
        self.timeout = timeout
        self.logger = logger

        self.messages: list[ClaudeMessage] = []
    
    def _chat_gen(self, messages: list[ClaudeMessage], **kwargs) -> Generator[str, None, None]:
        client = Anthropic()
        chunks: list[str] = []

        system: str | list[TextBlockParam] | NotGiven = (
            self.system_prompt
        if self.cache else 
            [{'text': self.system_prompt, 'type': 'text', 'cache_control': {'type': 'ephemeral'}}]
        )

        with client.messages.stream(
            model=self.model,
            messages=messages,
            timeout=self.timeout,
            max_tokens=1000,
            system=system,
            **kwargs
        ) as gen:
            for chunk in gen.text_stream:
                chunks.append(chunk)
                yield chunk

        # save the agent response to the list of messages
        messages.append(ClaudeMessage(role=ClaudeRole.model, text=''.join(chunks)))
        self.messages = messages
    
    @overload
    def multishot(self, messages: list[ClaudeMessage], stream:Literal[True], **kwargs) -> Generator[str, None, None]: ...
    @overload
    def multishot(self, messages: list[ClaudeMessage], stream:Literal[False]=False, **kwargs) -> str: ...
    def multishot(self, messages: list[ClaudeMessage], stream:bool=False, **kwargs) -> Generator[str, None, None]|str:
        gen = self._chat_gen(messages, **kwargs)
        return gen if stream else ''.join([*gen])
    
    @overload
    def oneshot(self, query:str, stream:Literal[True], **kwargs) -> Generator[str, None, None]: ...
    @overload
    def oneshot(self, query:str, stream:Literal[False]=False, **kwargs) -> str: ...
    def oneshot(self, query:str, stream:bool=False, **kwargs) -> Generator[str, None, None]|str:
        self.clear_messages()
        self.messages.append(ClaudeMessage(role=ClaudeRole.user, text=query))
        return self.multishot(self.messages, stream=stream, **kwargs)

    @overload
    def message(self, message:str, stream:Literal[True], **kwargs) -> Generator[str, None, None]: ...
    @overload
    def message(self, message:str, stream:Literal[False]=False, **kwargs) -> str: ...
    def message(self, message:str, stream:bool=False, **kwargs) -> Generator[str, None, None]|str:
        self.messages.append(ClaudeMessage(role=ClaudeRole.user, text=message))
        return self.multishot(self.messages, stream=stream, **kwargs)
    
    def push_user_message(self, message:str):
        self.messages.append(ClaudeMessage(role=ClaudeRole.user, text=message))
 
    def push_assistant_message(self, message:str):
        self.messages.append(ClaudeMessage(role=ClaudeRole.model, text=message))
    
    def clear_messages(self):
        self.messages = []

    def set_system_prompt(self, system_prompt:str|NotGiven=NOT_GIVEN):
        self.system_prompt = system_prompt

    def count_tokens(self, message: str) -> int:
        client = Anthropic()

        res = client.messages.count_tokens(
            model=self.model,
            messages=[ClaudeMessage(role=ClaudeRole.user, text=message)]
        )
        return res.input_tokens

    def get_context_window_size(self) -> int:
        return claude_context_sizes[self.model]


########################################################################################




class GeminiConfig(TypedDict):
    provider: Literal['google']
    api_key: NotRequired[Annotated[str, 'The API key for the Gemini API']]
    model: Annotated[GeminiModel, 'The model to use for the Gemini API']
    ttl_seconds: NotRequired[Annotated[int, "The time-to-live in seconds for the Gemini API cache"]]
GEMINI_DEFAULTS = {
    'ttl_seconds': 1800
}


class GPTConfig(TypedDict):
    provider: Literal['openai']
    api_key: NotRequired[Annotated[str, 'The API key for the OpenAI API']]
    model: Annotated[OpenAIModel, 'The model to use for the OpenAI API']
GPT_DEFAULTS = {}


class ClaudeConfig(TypedDict):
    provider: Literal['anthropic']
    api_key: NotRequired[Annotated[str, 'The API key for the Anthropic API']]
    model: Annotated[ClaudeModel, 'The model to use for the Anthropic API']
CLAUDE_DEFAULTS = {}

LLMConfig = GeminiConfig | GPTConfig | ClaudeConfig

def validate_config(config: LLMConfig):
    """
    Validate a configuration for a drafter agent.

    Args:
        config (LLMConfig): The configuration to validate
    """
    if config['provider'] == 'google':
        config_type = GeminiConfig
    elif config['provider'] == 'openai':
        config_type = GPTConfig
    elif config['provider'] == 'anthropic':
        config_type = ClaudeConfig
    else:
        raise ValueError(f'Unknown provider "{config["provider"]}"')

    config_keys = set(config.keys())
    allowed_keys = set(config_type.__annotations__.keys())
    if not config_keys.issubset(allowed_keys):
        raise ValueError(f'Invalid {config_type.__name__} keys {config_keys - allowed_keys} for drafter config {config}')




# some convenience configs for ease of use
gpt_41: GPTConfig = {'provider': 'openai', 'model': 'gpt-4.1'}
gpt_4o: GPTConfig = {'provider': 'openai', 'model': 'gpt-4o'}
gpt_4o_mini: GPTConfig = {'provider': 'openai', 'model': 'gpt-4o-mini'}
o3_mini: GPTConfig = {'provider': 'openai', 'model': 'o3-mini'}
claude_37_sonnet: ClaudeConfig = {'provider': 'anthropic', 'model': 'claude-3-7-sonnet-latest'}
claude_35_sonnet: ClaudeConfig = {'provider': 'anthropic', 'model': 'claude-3-5-sonnet-latest'}
claude_35_haiku: ClaudeConfig = {'provider': 'anthropic', 'model': 'claude-3-5-haiku-latest'}
gemini_25_pro: GeminiConfig = {'provider': 'google', 'model': 'gemini-2.5-pro-exp-03-25'}
gemini_15_pro: GeminiConfig = {'provider': 'google', 'model': 'gemini-1.5-pro-001'}
gemini_15_flash: GeminiConfig = {'provider': 'google', 'model': 'gemini-1.5-flash-001'}


def set_openai_api_key(api_key:str|None=None):
    """
    Set the OpenAI API key for the OpenAI API. If no key provided, uses the environment variable OPENAI_API_KEY
    """
    # overwrite the environment variable if a key is provided
    if api_key is not None:
        os.environ['OPENAI_API_KEY'] = api_key

    # ensure that a key is set
    if os.environ.get('OPENAI_API_KEY') is None:
        raise ValueError('OpenAI API key not provided or set in environment variable OPENAI_API_KEY')

    # openai just looks at the environment key, or expects you to pass it in with the client.
    # it does not have a global way to set it anymore

def set_gemini_api_key(api_key:str|None=None):
    """
    Set the Gemini API key for the Gemini API. If no key provided, uses the environment variable GEMINI_API_KEY
    """
    if api_key is not None:
        os.environ['GEMINI_API_KEY'] = api_key
    
    # ensure that a key is set
    if os.environ.get('GEMINI_API_KEY') is None:
        raise ValueError('Gemini API key not provided or set in environment variable GEMINI_API_KEY')
    
    # we manually have to pass the gemini api key into the genai library every time we make a client, so keep it in the environment variable
    
    # if api_key is None:
    #     api_key = os.environ.get('GEMINI_API_KEY')
    # if api_key is None:
    #     raise ValueError('Gemini API key not provided or set in environment variable GEMINI_API_KEY')
    # # pdb.set_trace()
    # # genai.configure(api_key=api_key)


def set_anthropic_api_key(api_key:str|None=None):
    """
    Set the Anthropic API key for the Anthropi API. If no key provided, uses the environment variable ANTHROPIC_API_KEY
    """
    if api_key is not None:
        os.environ['ANTHROPIC_API_KEY'] = api_key

    # ensure that a key is set
    if os.environ.get('ANTHROPIC_API_KEY') is None:
        raise ValueError('Anthropic API key not provided or set in environment variable ANTHROPIC_API_KEY')


def set_api_key(config: LLMConfig):
    """
    Set the API key given a model configuration.

    Args:
        config (LLMConfig): The configuration for the model
    """
    provider = config['provider']
    if provider == 'google':      set_gemini_api_key(config.get('api_key', None))
    elif provider == 'openai':    set_openai_api_key(config.get('api_key', None))
    elif provider == 'anthropic': set_anthropic_api_key(config.get('api_key', None))
    else:
        raise ValueError(f'Unknown provider "{provider}"')

