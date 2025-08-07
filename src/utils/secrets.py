"""
Secrets loader: environment-first, fallback to Vault (stub).
"""

import os
import logging

logger = logging.getLogger(__name__)

def get_secret(name: str) -> str:
    """
    Retrieve secret by name.

    Priority:
      1. ENV var
      2. (Stub) Vault lookup—raise if not found.

    Args:
        name: Secret key (e.g. "API_KEY").

    Returns:
        Secret value.

    Raises:
        KeyError if not present.
    """
    val = os.getenv(name)
    if val:
        return val
    # TODO: integrate with Vault or AWS Secrets Manager here
    logger.error(f"Secret {name} not found in environment")
    raise KeyError(f"Secret {name} not configured")
