"""
Type stubs for utility functions.
"""

import asyncio
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from GitFleet.providers.base import ProviderType
from GitFleet.utils.auth import CredentialEntry, CredentialManager
from GitFleet.utils.rate_limit import RateLimiter, rate_limited, RateLimitError
from GitFleet.utils.converters import to_dict, to_json, to_dataframe, flatten_dataframe

__all__ = [
    # Authentication utilities
    "CredentialManager",
    "CredentialEntry",
    # Rate limiting utilities
    "RateLimiter",
    "rate_limited",
    "RateLimitError",
    # Data conversion utilities
    "to_dict",
    "to_json",
    "to_dataframe",
    "flatten_dataframe",
]
