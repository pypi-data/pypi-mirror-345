from ..llmwraper.models import UsageMetric

def usage_metric_parser(response: dict) -> UsageMetric:
    """
    Parses the usage metric from the OpenAI API response.

    Args:
        response (dict): The response from the OpenAI API.

    Returns:
        dict: A dictionary containing the usage metric.
    """
    if "usage" in response:
        return UsageMetric(
            input_tokens=response["usage"].get("prompt_tokens", 0),
            output_tokens=response["usage"].get("completion_tokens", 0),
            total_tokens=response["usage"].get("total_tokens", 0),
            raw=response["usage"]
        )
    return  UsageMetric(
        input_tokens=0,
        output_tokens=0,
        total_tokens=0,
        raw={}
        )