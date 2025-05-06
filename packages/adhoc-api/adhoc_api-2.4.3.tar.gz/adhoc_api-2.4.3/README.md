# Ad-Hoc API
An [Archytas](https://github.com/jataware/archytas) tool that uses LLMs to interact with APIs given documentation. The user explains what they want in plain english, and then the agent (using the APIs docs for context) writes python code to complete the task.

## Installation
```bash
pip install adhoc-api
```

## Minimal Example

Here is a complete example of grabbing the HTML content of an API documentation page, converting it to markdown, and then having the adhoc-api tool interact with the API using the generated markdown documentation (see [examples/jokes.py](examples/jokes.py) for reference):

```python
from archytas.react import ReActAgent, FailedTaskError
from archytas.tools import PythonTool
from easyrepl import REPL
from adhoc_api.tool import AdhocApi, APISpec
from adhoc_api.uaii import claude_37_sonnet

from bs4 import BeautifulSoup
import requests
from markdownify import markdownify


def main():    
    # set up the API spec for the JokeAPI
    gdc_api: APISpec = {
        'name': "JokesAPI",
        'description': 'JokeAPI is a REST API that serves uniformly and well formatted jokes.',
        'documentation': get_joke_api_documentation(),
    }

    # set up the tools and agent
    adhoc_api = AdhocApi(apis=[gdc_api], drafter_config=claude_37_sonnet)
    python = PythonTool()
    agent = ReActAgent(model='gpt-4o', tools=[adhoc_api, python], verbose=True)

    # REPL to interact with agent
    for query in REPL(history_file='.chat'):
        try:
            answer = agent.react(query)
            print(answer)
        except FailedTaskError as e:
            print(f"Error: {e}")


def get_joke_api_documentation() -> str:
    """Download the HTML of the joke API documentation page with soup and convert it to markdown."""
    url = 'https://sv443.net/jokeapi/v2/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    markdown = markdownify(str(soup))
    
    return markdown


if __name__ == "__main__":
    main()
```

Then you can run the script and interact with the agent in the REPL:

```
$ python example.py

>>> Can you tell me what apis are available?
The available API is JokesAPI, which is a REST API that serves uniformly and well formatted jokes.

>>> Can you fetch a safe joke?
Here is a safe joke from the JokesAPI:

Category: Pun
Type: Two-part
Setup: What kind of doctor is Dr. Pepper?
Delivery: He's a fizzician.
```

## Library Interface

### AdhocApi
Instances of this tool are created via the `AdhocApi` class

```python
from adhoc_api.tool import AdhocApi

tool = AdhocApi(
    apis =                  # list[APISpec]: list of the APIs this tool can access
    drafter_config =        # LLMConfig | list[LLMConfig]: LLM model(s) to use for interacting with APIs
# ------------------------- # -------------------------
    curator_config =        # (optional) LLMConfig | None: LLM model for finding pre-existing solutions
    contextualizer_config = # (optional) LLMConfig | None: LLM model that supports the curator
    logger =                # (optional) Logger: logger instance
)
```

> Note: If multiple `LLMConfig`'s are provided in a list, the tool selects (per each API) the first model with a large enough context window.

> Note: If `curator_config` is set to `None`, the curation step will be skipped. Default is o3-mini, so you have to manually set it to `None` if you want that behavior

### LLMConfig
Specify which LLM model to use for drafting code. The config is simply a dictionary with the following fields:

```python
from adhoc_api.uaii import LLMConfig, GeminiConfig, GPTConfig, ClaudeConfig

# LLMConfig is just an alias for GeminiConfig | GPTConfig | ClaudeConfig
drafter_config: LLMConfig = {
    'provider': # 'openai' | 'google' | 'anthropic'
    'model':    # str: name of the model
    'api_key':  # (optional) str: manually set the API key here
}
```


Currently support the following providers and models:
- openai
    - gpt-4o
    - gpt-4o-mini
    - o1
    - o1-preview
    - o1-mini
    - gpt-4
    - gpt-4-turbo
- google
    - gemini-1.5-flash-001
    - gemini-1.5-pro-001
- anthropic
    - claude-3-5-sonnet-latest
    - claude-3-5-haiku-latest

Additionally depending on the provider, there might be extra fields supported in the `LLMConfig`. For example gemini models support `ttl_seconds` for specifying how long content is cached for. See the full type definitions of `GeminiConfig`, `GPTConfig`, and `ClaudeConfig` in [adhoc_api/uaii.py](adhoc_api/uaii.py)

Some examples of commonly used configs:
```
{'provider': 'openai', 'model': 'gpt-4o'}
{'provider': 'anthropic', 'model': 'claude-3-5-sonnet-latest'}
{'provider': 'google', 'model': 'gemini-1.5-pro-001'}
{'provider': 'google', 'model': 'gemini-1.5-flash-001', 'ttl_seconds': 1800},
```

This library also provides a few pre-made configs for convenience:

```python
from adhoc_api.uaii import (
    gpt_4o,
    gpt_4o_mini, 
    o3_mini,
    claude_37_sonnet,
    claude_35_sonnet,
    claude_35_haiku,
    gemini_15_pro,
    gemini_15_flash
)

# use any of these anywhere an LLMConfig is expected
```

### APISpec
Dictionary interface for representing an API

```python
from adhoc_api.tool import APISpec

spec: APISpec = {
    'name':           # str: Name of the API. This should be unique
    'description':    # str: A Description of the API
    'documentation':  # str: arbitrary documentation describing how to use the API
    'cache_key':      # (optional) str: (if possible) enable caching for this API
    'model_override': # (optional) LLMConfig: explicit model to use for this API
    'examples':       # (optional) list[Example]: examples of using the API
}
```

> Note: `description` is only seen by the archytas agent, not the drafter. Any content meant for the drafter should be provided in `documentation`.

### Example Curation
When loading an API into this library, you may provide code examples of using the API to solve various tasks. When the user makes a query, these examples will be used 2 ways:, 
1. If there is a perfect matching example that exactly solves the user's query, that example will be returned verbatim without consulting the drafter agent
1. If there are examples that are related to the query but are not perfect matches, they will be included with the user query and sent to the drafter so that the drafter can reference them when writing the solution. This allows the drafter to lean on known good flows rather than starting from scratch

When creating an instance of `AdhocApi`, you may optionally provide a `curator_config`, and a `contextualizer_config`. These specify which agents perform the curation process (by default, these are set to `o3-mini` and `gpt-4o` respectively).
- **The Curator**: looks at the current query and decides if any of the examples are perfect matches, or close matches, or no matches at all. For this task, it is recommended to use a model that can strongly reason about code behavior before making a decision like current chain-of-thought models like `o1`, `o3-mini`, etc.
- **The Contextualizer**: is used to convert the current user query into one that is context-free (i.e. no information from the prior conversation is necessary to understand the query). This is so the curator can focus on finding matches without potentially unrelated content from the chat history. This task does not require a particularly beefy model, merely one that is effective at summarizing whole conversations, hence the default of `gpt-4o`


### Automatically Selecting the Best model for each API
Ad-Hoc API supports automatically selecting the best model to use with a given API. At the moment this only looks at the length of the API documentation in tokens compared to the model context window size.

To use automatic selection, simply provide a list of configs for `drafter_config` when instantiating `AdhocApi`. For each API, the first suitable model in the list will be selected. If no models are suitable, an error will be raised (at `AdhocApi` instantiation time).

```python
from adhoc_api.tool import AdhocApi

tool = AdhocApi(apis = [...],
    drafter_config = [
        # better model but with smaller context window
        {'provider': 'anthropic', 'model': 'claude-3-5-sonnet-latest'},
        # worse model but supports largest context window
        {'provider': 'google', 'model': 'gemini-1.5-pro-001'}
    ]
)
```

### Using different models per API
In an `APISpec` you can explicitly indicate which model to use by specifying a `model_override`. This will ignore any model(s) specified when the `AdhocApi` instance was created.

```python
from adhoc_api.tool import APISpec, AdhocApi

# Only use claude for this API. Ignore any other models specified
spec_that_uses_gpt: APISpec = {
    'name': ...,
    'description': ...,
    'documentation': ...,
    'model_override': {'provider': 'anthropic', 'model': 'claude-3-7-sonnet-latest'}
}

# a bunch of other APIs that don't override the model
other_specs: list[APISpec] = [
    # ... other APIs ...
]

# create the instance of the AdhocAPI tool.
# All other APIs will use gemini specified in here
tool = AdhocApi(
    apis=[spec_that_uses_gpt, *other_specs],
    drafter_config={'provider': 'google', 'model': 'gemini-1.5-pro-001'}
)
```

### Loading APIs from YAML
For convenience, Ad-Hoc API supports loading `APISpec` dictionaries directly from yaml files. To use, your yaml file must include all required fields from the `APISpec` type definition, namely `name`, `description`, and `documentation`. You may include the optional fields as well i.e. `cache_key`, `model_override`, and `examples`.

```yaml
name: "Name of this API"
description: "Description of this API"
documentation: |
    all of the documentation 
    for this API, contained
    in a single string
# [optional fields]
# cache_key: ...
# model_override:
#    provider: ...
#    model: ...
# examples:
#    - query: ...
#      code: ...
#      notes: ...
#    - query:
#      code: ...
#    ...
```

yaml `APISpec`'s may be loaded via the following convenience function

```python
from adhoc_api.loader import load_yaml_api
from pathlib import Path

yaml_path = Path('location/of/the/api.yaml')
spec = load_yaml_api(yaml_path)
```

For convenience the yaml loader supports several tags for loading and manipulating content. The following tags are supported:
- `!load_txt`: replaces the given file path with raw text the contents of that file
- `!load_yaml`: replaces the given file path with the structured yaml loaded from the specified file (sub-yaml files may make use of these tags themselves)
- `!load_json`: replaces the given file path with the structured json loaded from the specified file
- `!fill`: interpolates the given string with values from the surrounding yaml file. For example, a string like `'this is an {interpolated} string'` would search the surrounding yaml for a field named `interpolated` and insert the value if present. Only values in the local file can be used (i.e. loading sub-files with `!load_yaml` will have no effect on this process)

Here's an example yaml representing some API specification:

```yaml
name: Name of this API
description: !fill This is {name}. It allows you to ...
documentation: !fill |
    # API Documentation
    {raw_documentation}


    # Usage Instructions
    some instructions on how to use this API
    etc.
    etc.

    ## Facets
    when using this API, ensure any enums/values are drawn from this list of facets:
    {facets}

raw_documentation: !load_txt documentation.md
facets: !load_txt facets.txt
examples: !load_yaml examples.yaml
```

> Note: when using `load_yaml_api`, any extra fields not in `APISpec` are ignored, and are purely for convenience of constructing and pulling content into the yaml.

### Loading Examples from YAML
It is recommended to store examples for APIs in a dedicated `examples.yaml` file, which should take the following form:

```yaml
- query: "text representing the task the user requested to be solved..."
  code: |
      # raw code that solves the above task
      ...
  notes: |
      (optional) notes that provide further explanation for how this 

- query: 'a different user request for this API'
  code: |
      # code for solving this task
      ...
  # no notes for this example

- # more examples  
```

I.e. it is a yaml where the top level is a list of items each with keys `query`, `code`, and optionally `notes`.

The most convenient way to include examples in an API is to make use of the `!load_yaml` tag to directly load the examples into the specification

```yaml
name: ...
description: ...
documentation: ...
examples: !load_yaml examples.yaml
```

If however you want the individual `Example` objects by themselves without loading an API, you may use the `load_yaml_examples` convenience function

```python
from adhoc_api.loader import load_yaml_examples
from pathlib import Path

path = Path('location/of/examples.yaml')
examples = load_yaml_examples(path)
```

### Setting API Keys
The preferred method of using API keys is to set them as an environment variable:
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GEMINI_API_KEY

Alternatively you can pass the key in as part of the `LLMConfig` via the `api_key` field as seen above.

### Caching
At present, prompt caching is supported by Gemini and Claude. Caching is done on a per API basis (because each API has different content that gets cached). To use caching, you must specify in the `APISpec` dict a unique `cache_key` (unique per all APIs in the system).

By default, gemini content is cached for 30 minutes after which the cache will be recreated if more messages are sent to the agent. You can override this amount by specifying an integer for `ttl_seconds` in the `LLMConfig`.

Claude caches content for 5 minutes and content is refreshed every time it is used. Currently there is no option for caching for longer--Instead Claude's caching is largely handled under the hood when Anthropic determines caching is possible

OpenAI models currently do not support caching in this library.
