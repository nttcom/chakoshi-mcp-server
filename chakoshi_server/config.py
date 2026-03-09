import os
from types import SimpleNamespace

def _load_config_internal() -> SimpleNamespace:
    """
    Loads and validates configuration settings from environment variables.
    Called from server.py.

    Returns:
        SimpleNamespace: An object containing the configuration settings.

    Raises:
        RuntimeError: If any required environment variable is not set or
                      if CHAKOSHI_TIMEOUT_SEC cannot be converted to an integer.
    """
    conf = SimpleNamespace()

    # Load each environment variable
    conf.api_key = os.getenv("CHAKOSHI_API_KEY")
    conf.api_url = os.getenv("CHAKOSHI_API_URL")
    conf.guardrail_id = os.getenv("CHAKOSHI_GUARDRAIL_ID")
    timeout_sec_str = os.getenv("CHAKOSHI_TIMEOUT_SEC")

    # Check for required environment variables
    if not conf.api_key:
        raise RuntimeError("Environment variable CHAKOSHI_API_KEY is not set")
    if not conf.api_url:
        raise RuntimeError("Environment variable CHAKOSHI_API_URL is not set")
    if not conf.guardrail_id:
        raise RuntimeError("Environment variable CHAKOSHI_GUARDRAIL_ID is not set")
    if not timeout_sec_str:
        raise RuntimeError("Environment variable CHAKOSHI_TIMEOUT_SEC is not set")

    # Convert timeout_sec to an integer
    try:
        conf.timeout_sec = int(timeout_sec_str)
    except ValueError:
        raise RuntimeError(f"Cannot convert environment variable CHAKOSHI_TIMEOUT_SEC ('{timeout_sec_str}') to an integer")

    return conf

# Load configuration settings when the module is imported
settings = _load_config_internal()
