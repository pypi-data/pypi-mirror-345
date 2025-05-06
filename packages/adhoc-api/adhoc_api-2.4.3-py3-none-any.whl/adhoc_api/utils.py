from typing import Protocol, Any, Generator
import os
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager


class Logger(Protocol):
    def debug(self, message: Any) -> None: ...
    def info(self, message: Any) -> None: ...
    def error(self, message: Any) -> None: ...

class SimpleLogger:
    def debug(self, message: Any) -> None:
        print('DEBUG', message)
    def info(self, message: Any) -> None:
        print('INFO', message)
    def error(self, message: Any) -> None:
        print('ERROR', message)


def extract_code_blocks(text: str) -> list[str]:
    """
    Extracts code blocks from a string of text
    Code blocks will be a between a pair of triple backticks ``` with optional language specifier after the first set
    """
    blocks = []
    in_block = False
    block = []
    for line in text.split('\n'):
        if line.startswith('```'):
            if in_block:
                blocks.append('\n'.join(block))
                block = []
            in_block = not in_block
        elif in_block:
            block.append(line)
    return blocks


def get_code(text: str, allow_multiple:bool=True) -> str:
    """
    Extracts raw code from any markdown code blocks in the text if present
    If multiple code blocks are present, they will be combined into a single source code output.
    If no code blocks are present, the original text will be returned as is.

    Args:
        text (str): The text to extract code from
        allow_multiple (bool): If False, will raise an error if multiple code blocks are found. Default is True.

    Returns:
        str: The extracted code as a string
    """
    code_blocks = extract_code_blocks(text)
    if len(code_blocks) == 0:
        return text
    if len(code_blocks) == 1:
        return code_blocks[0]
    if not allow_multiple:
        raise ValueError(f'Multiple code blocks found in text, but expected only one. Raw text:\n{text}')
    return '\n\n'.join(code_blocks)


def markdown_examples_to_py_list(examples_md: str) -> list[str]:
    ...
def yaml_examples_to_py_list(examples_yaml_path: Path) -> list[str]:
    ...

@contextmanager
def move_to_isolated_dir(prefix:str='workdir_') -> Generator[None, None, None]:
    """
    Context to create a unique isolated directory for working in, and move cd into it (and exit on context end)

    Args:
        prefix (str): Prefix for the directory name. A timestamp will be appended to this prefix.
    """
    original_dir = Path.cwd()
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        isolated_dir = Path(f'{prefix}{timestamp}')
        isolated_dir.mkdir(exist_ok=True)
        os.chdir(isolated_dir)
        yield
    finally:
        os.chdir(original_dir)
        # Optionally, remove the isolated directory if empty
        if not os.listdir(isolated_dir):
            os.rmdir(isolated_dir)


# TODO: do typing correctly on this
# type[T from TypedDict]
# dict that is T from TypedDict
# TODO: also consider replacing with from pydantic import TypeAdapter; adapter = TypeAdapter(t); adapter.validate_python(d)
def validate_typed_dict(t: type, d: dict, *, display_override: dict = {}):
    """
    Validate that the keys in the given dictionary are a subset of the keys in the TypedDict type.
    Raises ValueError if there are any invalid keys.

    Args:
        t (type): The TypedDict type to validate against.
        d (dict): The dictionary to validate.
        display_override (dict): A dictionary of values that mask actual values in the input dictionary.
            Use for display purposes, e.g. if a value in the input is too long to display, or sensitive, or etc.
    """
    # TODO: handle required vs optional!
    # TODO: recurse into nested TypedDicts
    allowed_keys = set(t.__annotations__.keys())
    given_keys = set(d.keys())
    if not given_keys.issubset(allowed_keys):
        truncated_d = {**d, **display_override}
        raise ValueError(f'Invalid keys {given_keys - allowed_keys} for "{t.__name__}" typed dict: {truncated_d}')



def strip_quotes(s: str) -> str:
    """strip quotes wrapping a string, repeatedly until string is bare"""
    while len(s) > 1 and s[0] == s[-1] and s[0] in ['"', "'", '`']:
        s = s[1:-1]
    return s



def truncate(s: str, max_len: int) -> str:
    """truncate a string to a maximum length"""
    if len(s) > max_len:
        return s[:max_len] + '...'
    return s