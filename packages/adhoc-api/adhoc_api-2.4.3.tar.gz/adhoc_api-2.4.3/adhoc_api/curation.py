"""
A bunch of utilities for dealing with examples
"""
from pathlib import Path
from typing import TypedDict
from typing_extensions import Annotated, NotRequired
from .utils import validate_typed_dict

import pdb

class Example(TypedDict):
    query: Annotated[str, 'The user query that is solved by this example.']
    code: Annotated[str, 'The code that solves the example.']
    notes: NotRequired[Annotated[str, 'Optional notes about the example.']]


def validate_example(example: Example):
    validate_typed_dict(Example, example)


def examples_to_str(examples: list[Example], *, title_header: str = 'Relevant Examples', example_header: str = 'Example') -> str:
    """
    Convert a list of examples to a markdown string representation.

    Args:
        examples (list[Example]): A list of Example objects.
        title_header (str, optional): The header for the examples section. Defaults to 'Relevant Examples'.

    Returns:
        str: A markdown string representation of the examples.
    """
    # build up the string containing the examples
    examples_chunks = [f'# {title_header}']
    for i, example in enumerate(examples, start=1):
        example_chunks = []
        example_chunks.append(f'## {example_header} {i}: {example["query"]}')
        if 'notes' in example: example_chunks.append(f'### Notes\n{example["notes"]}')
        example_chunks.append(f'### Code:\n```python\n{example["code"]}\n```')
        examples_chunks.append('\n'.join(example_chunks))
    examples_str = '\n\n'.join(examples_chunks)

    return examples_str



def convert_examples_md_to_yaml(examples_md_path: Path) -> str:
    pdb.set_trace()
    ...

def example_md_to_yaml(example_md: str) -> str:
    pdb.set_trace()
    ...