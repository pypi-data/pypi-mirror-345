from json import JSONDecodeError
from typing import Dict

from llmforge.exceptions import OutputParsingError

from ..utils import TLLMBaseModel

from .utils import parse_json_markdown

def json_parser(llm_response_content: str) -> Dict:
    """
    Parses a string containing JSON content and returns it as a dictionary.

    This function first strips any leading or trailing whitespace from the input
    string and then attempts to parse it as JSON using the `parse_json_markdown` function.
    If the parsing fails due to a JSON decoding error, an `OutputParsingError` is raised
    with the original response content.

    Args:
        llm_response_content (str): The string containing the JSON content to be parsed.

    Returns:
        Dict: The parsed JSON content as a dictionary.

    Raises:
        OutputParsingError: If the input string cannot be parsed as valid JSON.
    """
    llm_response_content = llm_response_content.strip()
    try:
        return parse_json_markdown(llm_response_content)
    except JSONDecodeError as e:
        raise OutputParsingError(response=llm_response_content)

def pydantic_parser(llm_response_content: str, model: type[TLLMBaseModel]) -> TLLMBaseModel:
    """
    Parses a JSON-formatted LLM response and validates it against a Pydantic model.

    Args:
        llm_response_content (str): The JSON string response from the LLM.
        model (type[TLLMBaseModel]): The Pydantic model class to validate the parsed data against.

    Returns:
        TLLMBaseModel: An instance of the provided Pydantic model populated with the parsed data.

    Raises:
        ValidationError: If the parsed data does not conform to the Pydantic model schema.
        JSONDecodeError: If the input string is not valid JSON.
    """
    parsed_data = json_parser(llm_response_content)
    return model(**parsed_data)