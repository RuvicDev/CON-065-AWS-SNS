---
name: aws_sns
description: "Usa la librería ruvic_aws_sns_connector para publicar notificaciones en topics SNS, listar topics y enviar SMS mediante Amazon SNS. Úsala cuando el usuario pida publicar mensajes, notificaciones o SMS con AWS SNS. El envío SMS está bloqueado por defecto y requiere autorización explícita."
triggers:
- aws sns
- sns
- amazon sns
- topic
- publicar notificación
- sms
---

# Conector AWS SNS (ruvic_aws_sns_connector)

## Regla crítica de credenciales

El código generado NUNCA hardcodea credenciales. Siempre se leen de variables de entorno:

| Variable | Contenido |
|---|---|
| `RUVIC_AWS_SNS_AWS_ACCESS_KEY_ID` | Access Key ID de AWS |
| `RUVIC_AWS_SNS_AWS_SECRET_ACCESS_KEY` | Secret Access Key de AWS |
| `RUVIC_AWS_SNS_AWS_SESSION_TOKEN` | Token STS opcional |
| `RUVIC_AWS_SNS_REGION` | Región AWS |
| `RUVIC_AWS_SNS_DEFAULT_TOPIC_ARN` | Topic ARN opcional por defecto |
| `RUVIC_AWS_SNS_ALLOW_SMS` | Debe ser true para permitir SMS |
| `RUVIC_AWS_SNS_SMS_SENDER_ID` | Sender ID opcional |
| `RUVIC_AWS_SNS_SMS_TYPE` | Transactional o Promotional |
| `RUVIC_AWS_SNS_TIMEOUT` | Timeout opcional |
| `RUVIC_AWS_SNS_MAX_MESSAGE_LENGTH` | Límite opcional de bytes por mensaje |

Si estas variables NO existen, el conector no está configurado: no generes código que lo use; indica al usuario que lo configure en Settings → Conectores. Nunca uses variables con alias `_DEFAULT_`, `_TEST_` o `_PRODUCCION_`.

## Conexión

```python
from ruvic_aws_sns_connector import AwsSnsClient
client = AwsSnsClient()
```

## Capacidad 1 — Publicar en topic

```python
result = client.publish_to_topic(
    message="Pedido creado correctamente",
    topic_arn="arn:aws:sns:us-east-1:123456789012:pedidos",
    subject="Nuevo pedido",
)
print(result["message_id"])
```

## Capacidad 2 — Listar topics

```python
topics = client.list_topics(max_results=20)
for topic in topics:
    print(topic["topic_arn"])
```

## Capacidad 3 — Enviar SMS

Antes de enviar SMS reales, confirma número, mensaje, costo y autorización. Esta capacidad requiere `RUVIC_AWS_SNS_ALLOW_SMS=true`.

```python
result = client.send_sms(
    phone_number="+573001234567",
    message="Tu código de verificación es 123456",
)
print(result["message_id"])
```

## Manejo de errores

```python
from ruvic_aws_sns_connector import AwsSnsAuthError, AwsSnsConfigError, AwsSnsDataError, AwsSnsNetworkError, AwsSnsSecurityError
try:
    client.publish_to_topic("Hola", topic_arn="arn:aws:sns:...")
except AwsSnsConfigError as exc:
    print(f"Configuración inválida: {exc}")
except AwsSnsAuthError:
    print("Credenciales o permisos IAM inválidos para AWS SNS")
except AwsSnsNetworkError:
    print("No se pudo alcanzar AWS SNS")
except AwsSnsSecurityError as exc:
    print(f"Operación bloqueada: {exc}")
except AwsSnsDataError as exc:
    print(f"AWS SNS rechazó la solicitud: {exc}")
```

## Buenas prácticas al generar código

1. Lee credenciales SOLO de `RUVIC_AWS_SNS_*`.
2. Nunca imprimas access keys, secret keys ni tokens.
3. Confirma con el usuario antes de publicar mensajes que disparen notificaciones reales.
4. No envíes SMS salvo que `ALLOW_SMS` esté activado y el usuario confirme costo/destino.
5. Usa mensajes cortos y evita datos sensibles en SMS.
