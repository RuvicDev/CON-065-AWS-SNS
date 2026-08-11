"""Cliente para AWS SNS.

Capacidades:
- publish_to_topic(): publicar un mensaje en un topic SNS.
- list_topics(): listar topics SNS.
- send_sms(): enviar SMS mediante SNS, bloqueado por defecto por costo/impacto.
"""
from __future__ import annotations
import json
import re
from typing import Any
import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError, ConnectTimeoutError, EndpointConnectionError, ReadTimeoutError
from .config import AwsSnsConfig
from .exceptions import AwsSnsAuthError, AwsSnsDataError, AwsSnsNetworkError, AwsSnsSecurityError
from .logging_utils import get_logger

_PHONE_RE = re.compile(r"^\+[1-9][0-9]{7,14}$")

class AwsSnsClient:
    """Cliente para publicación de notificaciones con AWS SNS.

    Args:
        config: configuración opcional. Si se omite, lee RUVIC_AWS_SNS_*.

    Ejemplo:
        >>> client = AwsSnsClient()
        >>> client.list_topics()
        [{'topic_arn': 'arn:aws:sns:us-east-1:123456789012:mi-topic'}]
    """
    def __init__(self, config: AwsSnsConfig | None = None) -> None:
        self.config = config or AwsSnsConfig.from_env()
        self._logger = get_logger()
        self._sns = self._build_sns_client()

    def _build_sns_client(self):
        boto_config = BotoConfig(connect_timeout=self.config.timeout, read_timeout=self.config.timeout, retries={"max_attempts": 3, "mode": "standard"})
        session = boto3.Session(aws_access_key_id=self.config.aws_access_key_id, aws_secret_access_key=self.config.aws_secret_access_key, aws_session_token=self.config.aws_session_token, region_name=self.config.region)
        return session.client("sns", config=boto_config)

    def _handle_client_error(self, exc: ClientError) -> None:
        error = exc.response.get("Error", {})
        code = error.get("Code", "Unknown")
        message = error.get("Message", str(exc))
        if code in {"AuthFailure", "AccessDenied", "AccessDeniedException", "InvalidClientTokenId", "SignatureDoesNotMatch", "UnrecognizedClientException", "ExpiredToken", "AuthorizationError"}:
            raise AwsSnsAuthError(f"AWS SNS rechazó credenciales o permisos ({code}). Revisa access key, secret, región y permisos IAM sns:Publish y sns:ListTopics.") from exc
        if code in {"InvalidParameter", "InvalidParameterValue", "NotFound", "NotFoundException", "EndpointDisabled", "KMSAccessDenied", "Throttled", "Throttling", "ThrottlingException", "OptedOut"}:
            raise AwsSnsDataError(f"AWS SNS rechazó la solicitud ({code}): {message}. Verifica topic ARN, teléfono, atributos y límites SNS/SMS.") from exc
        raise AwsSnsDataError(f"AWS SNS retornó un error ({code}): {message}.") from exc

    def _call(self, operation: str, **kwargs: Any) -> dict[str, Any]:
        try:
            return getattr(self._sns, operation)(**kwargs)
        except (EndpointConnectionError, ConnectTimeoutError, ReadTimeoutError) as exc:
            raise AwsSnsNetworkError(f"No se pudo conectar con AWS SNS en región {self.config.region}. Verifica región, red, DNS y firewall.") from exc
        except ClientError as exc:
            self._handle_client_error(exc)
            raise AssertionError("unreachable")
        except BotoCoreError as exc:
            raise AwsSnsNetworkError(f"Error de comunicación con AWS SNS: {exc}.") from exc

    def _validate_message(self, message: str) -> None:
        if not message or not message.strip():
            raise AwsSnsDataError("El mensaje no puede estar vacío.")
        if len(message.encode("utf-8")) > self.config.max_message_length:
            raise AwsSnsSecurityError(f"Mensaje bloqueado: excede RUVIC_AWS_SNS_MAX_MESSAGE_LENGTH={self.config.max_message_length} bytes.")

    def ping(self) -> bool:
        """Verifica credenciales y acceso básico listando un topic como máximo.

        Returns:
            True si AWS SNS responde.
        Ejemplo:
            >>> client.ping()
            True
        """
        self._call("list_topics")
        self._logger.info("Ping exitoso a AWS SNS en región %s", self.config.region)
        return True

    def list_topics(self, max_results: int = 100) -> list[dict[str, str]]:
        """Lista topics SNS de la cuenta/región.

        Args:
            max_results: máximo de topics a retornar.
        Returns:
            Lista de dicts con `topic_arn`.
        Ejemplo:
            >>> client.list_topics(max_results=10)
            [{'topic_arn': 'arn:aws:sns:us-east-1:123456789012:mi-topic'}]
        """
        max_results = max(1, min(int(max_results), 1000))
        topics: list[dict[str, str]] = []
        next_token: str | None = None
        while len(topics) < max_results:
            kwargs: dict[str, Any] = {}
            if next_token:
                kwargs["NextToken"] = next_token
            response = self._call("list_topics", **kwargs)
            for topic in response.get("Topics", []):
                topics.append({"topic_arn": topic.get("TopicArn", "")})
                if len(topics) >= max_results:
                    break
            next_token = response.get("NextToken")
            if not next_token:
                break
        self._logger.info("Listados %d topics SNS", len(topics))
        return topics

    def publish_to_topic(self, message: str, topic_arn: str | None = None, subject: str | None = None, message_attributes: dict[str, str] | None = None) -> dict[str, str]:
        """Publica un mensaje en un topic SNS.

        Args:
            message: contenido del mensaje.
            topic_arn: ARN del topic. Si se omite, usa RUVIC_AWS_SNS_DEFAULT_TOPIC_ARN.
            subject: asunto opcional para protocolos que lo soporten.
            message_attributes: atributos string opcionales.
        Returns:
            Dict con `message_id` y `topic_arn`.
        Ejemplo:
            >>> client.publish_to_topic("Pedido creado", topic_arn="arn:aws:sns:...")
            {'message_id': '...', 'topic_arn': 'arn:aws:sns:...'}
        """
        self._validate_message(message)
        resolved_topic = topic_arn or self.config.default_topic_arn
        if not resolved_topic:
            raise AwsSnsDataError("Debes indicar topic_arn o configurar RUVIC_AWS_SNS_DEFAULT_TOPIC_ARN.")
        payload: dict[str, Any] = {"TopicArn": resolved_topic, "Message": message}
        if subject:
            payload["Subject"] = subject[:100]
        if message_attributes:
            payload["MessageAttributes"] = {k: {"DataType": "String", "StringValue": str(v)} for k, v in message_attributes.items()}
        response = self._call("publish", **payload)
        message_id = response.get("MessageId", "")
        self._logger.info("Mensaje publicado en topic SNS")
        return {"message_id": message_id, "topic_arn": resolved_topic}

    def send_sms(self, phone_number: str, message: str, sender_id: str | None = None, sms_type: str | None = None) -> dict[str, str]:
        """Envía un SMS mediante AWS SNS.

        Esta operación está bloqueada por defecto porque puede generar costo e impacto real.
        Activa RUVIC_AWS_SNS_ALLOW_SMS=true para permitirla.

        Args:
            phone_number: teléfono en formato E.164, por ejemplo +573001234567.
            message: texto del SMS.
            sender_id: Sender ID opcional si el país lo soporta.
            sms_type: Transactional o Promotional.
        Returns:
            Dict con `message_id` y `phone_number`.
        Ejemplo:
            >>> client.send_sms("+573001234567", "Código 123456")
            {'message_id': '...', 'phone_number': '+573001234567'}
        """
        if not self.config.allow_sms:
            raise AwsSnsSecurityError("Envío SMS bloqueado por defecto. Activa RUVIC_AWS_SNS_ALLOW_SMS=true solo para pruebas o uso autorizado.")
        if not _PHONE_RE.match(phone_number):
            raise AwsSnsDataError("phone_number debe estar en formato E.164, por ejemplo +573001234567.")
        self._validate_message(message)
        resolved_type = sms_type or self.config.sms_type
        if resolved_type not in {"Transactional", "Promotional"}:
            raise AwsSnsDataError("sms_type debe ser Transactional o Promotional.")
        attributes = {"AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": resolved_type}}
        resolved_sender = sender_id or self.config.sms_sender_id
        if resolved_sender:
            attributes["AWS.SNS.SMS.SenderID"] = {"DataType": "String", "StringValue": resolved_sender[:11]}
        response = self._call("publish", PhoneNumber=phone_number, Message=message, MessageAttributes=attributes)
        message_id = response.get("MessageId", "")
        self._logger.info("SMS SNS enviado a número enmascarado")
        return {"message_id": message_id, "phone_number": phone_number}
