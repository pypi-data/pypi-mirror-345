from llmforge.llmwraper.models import UsageMetric


def cost_calculator(metric: UsageMetric, model: str) -> float:
    # Define pricing per million tokens
    pricing = {
        "gpt-4o": (2.50, 10.00),
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4.5": (75.00, 150.00),
        "gpt-4-turbo": (10.00, 30.00),
        "gpt-4": (30.00, 60.00),
        "gpt-4-32k": (60.00, 120.00),
        "o1": (15.00, 60.00),
        "o1-pro": (150.00, 600.00),
    }

    # Normalize model name to lowercase
    model_key = model.lower()

    # Retrieve pricing; default to (0.0, 0.0) if model not found
    input_cost_per_million, output_cost_per_million = pricing.get(model_key, (0.0, 0.0))

    # Calculate cost
    input_cost = (metric.input_tokens / 1_000_000) * input_cost_per_million
    output_cost = (metric.output_tokens / 1_000_000) * output_cost_per_million

    return input_cost + output_cost