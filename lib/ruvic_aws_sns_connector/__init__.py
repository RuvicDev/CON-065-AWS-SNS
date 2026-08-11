"""Conector Ruvic para AWS SNS."""
from .client import AwsSnsClient
from .config import ENV_PREFIX, AwsSnsConfig
from .exceptions import AwsSnsAuthError, AwsSnsConfigError, AwsSnsConnectorError, AwsSnsDataError, AwsSnsNetworkError, AwsSnsSecurityError
from .logging_utils import setup_logging
__all__ = ["ENV_PREFIX", "AwsSnsAuthError", "AwsSnsClient", "AwsSnsConfig", "AwsSnsConfigError", "AwsSnsConnectorError", "AwsSnsDataError", "AwsSnsNetworkError", "AwsSnsSecurityError", "setup_logging"]
__version__ = "1.0.0"
