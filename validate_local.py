"""Validación local del conector AWS SNS contra AWS real.

Requiere RUVIC_AWS_SNS_* apuntando a una cuenta AWS de prueba. Por defecto no
publica mensajes ni envía SMS reales. Para publicar, define RUN flags explícitos.
"""
from __future__ import annotations
import os
from ruvic_aws_sns_connector import AwsSnsClient, AwsSnsSecurityError, setup_logging
setup_logging("INFO")
client = AwsSnsClient()
print("== Ping =="); print(client.ping())
print("== Listar topics =="); topics = client.list_topics(max_results=10); print(f"Topics: {len(topics)}"); [print(f"  {t}") for t in topics]
print("== Bloqueo SMS por defecto ==")
try:
    client.send_sms("+573001234567", "Prueba que debe bloquearse")
except AwsSnsSecurityError as exc:
    print(f"  OK bloqueo confirmado: {exc}")
else:
    raise RuntimeError("FALLO: send_sms no se bloqueó")
if os.environ.get("RUVIC_AWS_SNS_RUN_PUBLISH_TESTS", "").lower() == "true":
    topic_arn = os.environ.get("RUVIC_AWS_SNS_TEST_TOPIC_ARN", "").strip() or client.config.default_topic_arn
    if not topic_arn:
        raise RuntimeError("RUN_PUBLISH_TESTS requiere RUVIC_AWS_SNS_TEST_TOPIC_ARN o DEFAULT_TOPIC_ARN")
    print("== Publicación real en topic ==")
    print(client.publish_to_topic("Prueba local Ruvic AWS SNS", topic_arn=topic_arn, subject="Prueba Ruvic"))
else:
    print("Publicación real omitida. Define RUVIC_AWS_SNS_RUN_PUBLISH_TESTS=true para publicar.")
if os.environ.get("RUVIC_AWS_SNS_RUN_SMS_TESTS", "").lower() == "true":
    phone = os.environ.get("RUVIC_AWS_SNS_TEST_PHONE_NUMBER", "").strip()
    if not phone:
        raise RuntimeError("RUN_SMS_TESTS requiere RUVIC_AWS_SNS_TEST_PHONE_NUMBER")
    print("== Envío SMS real =="); print(client.send_sms(phone, "Prueba local Ruvic AWS SNS"))
else:
    print("SMS real omitido. Define RUN_SMS_TESTS y ALLOW_SMS=true para enviar.")
