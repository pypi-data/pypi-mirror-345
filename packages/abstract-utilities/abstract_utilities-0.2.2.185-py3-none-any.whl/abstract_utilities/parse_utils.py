import os
import re
from abstract_utilities import write_to_file
from abstract_utilities.math_utils import find_common_denominator

def get_token_encoder(model_name: str = "gpt-4", encoding_name: str = None):
    import tiktoken
    """
    Retrieves the encoder for a given model or encoding name.
    
    Args:
        model_name (str): The name of the model. Defaults to "gpt-4".
        encoding_name (str, optional): The encoding name to use. If not provided, it defaults based on the model.

    Returns:
        Encoder: A tiktoken encoder object.
    """
    if encoding_name:
        return tiktoken.get_encoding(encoding_name)
    else:
        return tiktoken.encoding_for_model(model_name)

def num_tokens_from_string(string: str, model_name: str = "gpt-4", encoding_name: str = None) -> int:
    """
    Returns the number of tokens in a text string.

    Args:
        string (str): The input text.
        model_name (str, optional): The model name to determine encoding if encoding_name is not specified. Defaults to "gpt-4".
        encoding_name (str, optional): The encoding name to use. If not specified, uses model-based encoding.

    Returns:
        int: The count of tokens.
    """
    encoding = get_token_encoder(model_name, encoding_name)
    num_tokens = len(encoding.encode(str(string)))
    return num_tokens

def infer_tab_size(file_path):
    if not os.path.isfile(file_path):
        write_to_file(file_path=file_path, contents='\t')
    with open(file_path, 'r') as file:
        for line in file:
            if '\t' in line:
                return len(line) - len(line.lstrip())  # The length of indentation
    return 4  # Default if no tab found

def get_blocks(data, delim='\n'):
    if isinstance(data, list):
        return data, None
    if isinstance(data, tuple):
        data, delim = data[0], data[-1]
    return data.split(delim), delim

def get_indent_levels(text):
    tab_size, indent_list = infer_tab_size('config.txt'), [0]
    for line in text.split('\n'):
        indent = 0
        for char in line:
            if char in [' ', '\t']:
                indent += tab_size if char == '\t' else 1
            else:
                break
        if indent not in indent_list:
            indent_list.append(indent)
    return indent_list

def get_code_blocks(data, indent_level=0):
    blocks = [[]]
    lines, delim = get_blocks(data, '\n')
    for line in lines:
        beginning = ''
        for char in line:
            if char in ['', ' ', '\n', '\t']:
                beginning += char
            else:
                break
        if len(beginning) == indent_level:
            blocks[-1] = delim.join(blocks[-1])
            blocks.append([line])
        else:
            blocks[-1].append(line)
    blocks[-1] = delim.join(blocks[-1])
    return blocks, delim

def chunk_any_to_tokens(data, max_tokens, model_name="gpt-4", encoding_name=None, delimiter='\n\n', reverse=False):
    if isinstance(data, list):
        blocks = data
    else:
        blocks, delimiter = get_blocks(data, delimiter)

    if reverse:
        blocks = reversed(blocks)

    chunks = []
    current_chunk = []

    for block in blocks:
        if num_tokens_from_string(delimiter.join(current_chunk + [block]), model_name, encoding_name) <= max_tokens:
            current_chunk.append(block)
        else:
            if current_chunk:
                chunks.append(delimiter.join(current_chunk))
            current_chunk = [block]

    if current_chunk:
        chunks.append(''.join(current_chunk))

    return chunks

def chunk_data_by_type(data, max_tokens, chunk_type=None, model_name="gpt-4", encoding_name=None, reverse=False):
    delimiter = None
    if chunk_type == "URL":
        delimiter = None
        blocks = re.split(r'<h[1-6].*?>.*?</h[1-6]>', data)
    elif chunk_type == "SOUP":
        delimiter = None
        blocks = data
    elif chunk_type == "DOCUMENT":
        delimiter = "."
        blocks = data.split(delimiter)
    elif chunk_type == "CODE":
        return chunk_source_code(data, max_tokens, model_name, encoding_name, reverse=reverse)
    elif chunk_type == "TEXT":
        return chunk_text_by_tokens(data, max_tokens, model_name, encoding_name, reverse=reverse)
    else:
        delimiter = "\n\n"
        blocks = data.split(delimiter)
    
    return chunk_any_to_tokens(blocks, max_tokens, model_name, encoding_name, delimiter, reverse=reverse)

def chunk_text_by_tokens(prompt_data, max_tokens, model_name="gpt-4", encoding_name=None, reverse=False):
    sentences = prompt_data.split("\n")
    if reverse:
        sentences = reversed(sentences)

    chunks = []
    current_chunk = ""
    current_chunk_tokens = 0

    for sentence in sentences:
        sentence_tokens = num_tokens_from_string(sentence, model_name, encoding_name)

        if current_chunk_tokens + sentence_tokens <= max_tokens:
            current_chunk += "\n" + sentence if current_chunk else sentence
            current_chunk_tokens += sentence_tokens
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
            current_chunk_tokens = sentence_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def extract_functions_and_classes(source_code, reverse=False):
    functions_and_classes = []
    func_pattern = re.compile(r'^\s*def\s+\w+\s*\(.*\):')
    class_pattern = re.compile(r'^\s*class\s+\w+\s*\(.*\):')
    
    lines = source_code.splitlines()
    if reverse:
        lines = reversed(lines)

    current_block = []
    for line in lines:
        if func_pattern.match(line) or class_pattern.match(line):
            functions_and_classes.append("\n".join(current_block))
            current_block = []
        current_block.append(line)
    if current_block:
        functions_and_classes.append("\n".join(current_block))
    
    return functions_and_classes

def chunk_source_code(source_code, max_tokens, model_name="gpt-4", encoding_name=None, reverse=False):
    chunks = ['']
    functions_and_classes = extract_functions_and_classes(source_code, reverse=reverse)

    for block in functions_and_classes:
        if num_tokens_from_string(block, model_name, encoding_name) > max_tokens:
            chunks.extend(chunk_data_by_type(block, max_tokens, "CODE", model_name, encoding_name))
        elif num_tokens_from_string(chunks[-1] + block, model_name, encoding_name) > max_tokens:
            chunks.append(block)
        else:
            chunks[-1] += '\n' + block
    
    return chunks
