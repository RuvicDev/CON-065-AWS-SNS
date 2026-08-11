"""Excepciones propias del conector AWS SNS."""

class AwsSnsConnectorError(Exception):
    """Error base del conector AWS SNS."""

class AwsSnsConfigError(AwsSnsConnectorError):
    """Falta configuración requerida o algún valor de configuración es inválido."""

class AwsSnsAuthError(AwsSnsConnectorError):
    """Credenciales AWS inválidas, expiradas o permisos IAM insuficientes."""

class AwsSnsNetworkError(AwsSnsConnectorError):
    """Error de red, DNS, timeout o endpoint AWS SNS no alcanzable."""

class AwsSnsDataError(AwsSnsConnectorError):
    """Solicitud inválida, topic inexistente, teléfono inválido o límite SNS alcanzado."""

class AwsSnsSecurityError(AwsSnsConnectorError):
    """Operación bloqueada por reglas de seguridad del conector."""
