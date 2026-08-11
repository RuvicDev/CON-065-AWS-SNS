"""Configuración del conector leída desde variables de entorno.

Prefijo: RUVIC_AWS_SNS_
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from .exceptions import AwsSnsConfigError

ENV_PREFIX = "RUVIC_AWS_SNS_"

def _to_bool(value: str, default: bool = False) -> bool:
    raw = (value or "").strip().lower()
    if raw == "":
        return default
    if raw in {"true", "1", "yes", "y", "on"}:
        return True
    if raw in {"false", "0", "no", "n", "off"}:
        return False
    raise AwsSnsConfigError("Configuración inválida: los campos booleanos deben ser true/false.")

@dataclass(frozen=True)
class AwsSnsConfig:
    """Parámetros para autenticar y usar AWS SNS."""
    aws_access_key_id: str
    aws_secret_access_key: str
    region: str
    aws_session_token: str | None = None
    default_topic_arn: str | None = None
    sms_sender_id: str | None = None
    sms_type: str = "Transactional"
    allow_sms: bool = False
    timeout: int = 20
    max_message_length: int = 8192

    @classmethod
    def from_env(cls) -> "AwsSnsConfig":
        """Construye la configuración desde variables RUVIC_AWS_SNS_*.

        Raises:
            ValueError: si faltan variables requeridas.
            AwsSnsConfigError: si un valor opcional es inválido.

        Ejemplo:
            >>> config = AwsSnsConfig.from_env()
            >>> config.region
            'us-east-1'
        """
        aws_access_key_id = os.environ.get(f"{ENV_PREFIX}AWS_ACCESS_KEY_ID", "").strip()
        aws_secret_access_key = os.environ.get(f"{ENV_PREFIX}AWS_SECRET_ACCESS_KEY", "").strip()
        region = os.environ.get(f"{ENV_PREFIX}REGION", "").strip()
        missing = [n for n, v in ((f"{ENV_PREFIX}AWS_ACCESS_KEY_ID", aws_access_key_id), (f"{ENV_PREFIX}AWS_SECRET_ACCESS_KEY", aws_secret_access_key), (f"{ENV_PREFIX}REGION", region)) if not v]
        if missing:
            raise ValueError("Faltan variables de entorno del conector aws_sns: " + ", ".join(missing) + ". Configura el conector en Settings → Conectores.")
        try:
            timeout = int(os.environ.get(f"{ENV_PREFIX}TIMEOUT", "20").strip() or "20")
            max_message_length = int(os.environ.get(f"{ENV_PREFIX}MAX_MESSAGE_LENGTH", "8192").strip() or "8192")
            allow_sms = _to_bool(os.environ.get(f"{ENV_PREFIX}ALLOW_SMS", "false"), default=False)
        except ValueError as exc:
            raise AwsSnsConfigError("Configuración inválida: TIMEOUT y MAX_MESSAGE_LENGTH deben ser enteros.") from exc
        if timeout <= 0 or timeout > 120:
            raise AwsSnsConfigError("RUVIC_AWS_SNS_TIMEOUT debe estar entre 1 y 120 segundos.")
        if max_message_length <= 0 or max_message_length > 262144:
            raise AwsSnsConfigError("RUVIC_AWS_SNS_MAX_MESSAGE_LENGTH debe estar entre 1 y 262144 bytes.")
        sms_type = os.environ.get(f"{ENV_PREFIX}SMS_TYPE", "Transactional").strip() or "Transactional"
        if sms_type not in {"Transactional", "Promotional"}:
            raise AwsSnsConfigError("RUVIC_AWS_SNS_SMS_TYPE debe ser Transactional o Promotional.")
        return cls(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=os.environ.get(f"{ENV_PREFIX}AWS_SESSION_TOKEN", "").strip() or None,
            region=region,
            default_topic_arn=os.environ.get(f"{ENV_PREFIX}DEFAULT_TOPIC_ARN", "").strip() or None,
            sms_sender_id=os.environ.get(f"{ENV_PREFIX}SMS_SENDER_ID", "").strip() or None,
            sms_type=sms_type,
            allow_sms=allow_sms,
            timeout=timeout,
            max_message_length=max_message_length,
        )
