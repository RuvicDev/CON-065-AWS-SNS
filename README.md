# Conector AWS SNS para Ruvic

Conector Ruvic para publicar notificaciones y mensajes con Amazon Simple Notification Service (AWS SNS): publicar en topic, listar topics y enviar SMS.

## Capacidades

1. `publish_to_topic(message, topic_arn=None, subject=None, message_attributes=None)`.
2. `list_topics(max_results=100)`.
3. `send_sms(phone_number, message, sender_id=None, sms_type=None)` bloqueado por defecto.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./lib
```

Desde Git:

```bash
pip install git+https://github.com/montealegre777/conector-aws-sns.git#subdirectory=lib
```

## Variables de entorno

| Variable | Obligatoria | Descripción | Default |
|---|---:|---|---|
| `RUVIC_AWS_SNS_AWS_ACCESS_KEY_ID` | Sí | Access Key ID | — |
| `RUVIC_AWS_SNS_AWS_SECRET_ACCESS_KEY` | Sí | Secret Access Key | — |
| `RUVIC_AWS_SNS_AWS_SESSION_TOKEN` | No | Token STS temporal | — |
| `RUVIC_AWS_SNS_REGION` | Sí | Región AWS | — |
| `RUVIC_AWS_SNS_DEFAULT_TOPIC_ARN` | No | Topic ARN por defecto | — |
| `RUVIC_AWS_SNS_ALLOW_SMS` | No | Habilita SMS real | `false` |
| `RUVIC_AWS_SNS_SMS_SENDER_ID` | No | Sender ID para SMS | — |
| `RUVIC_AWS_SNS_SMS_TYPE` | No | Transactional o Promotional | `Transactional` |
| `RUVIC_AWS_SNS_TIMEOUT` | No | Timeout de red | `20` |
| `RUVIC_AWS_SNS_MAX_MESSAGE_LENGTH` | No | Máximo bytes por mensaje | `8192` |

## Permisos IAM mínimos

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["sns:ListTopics", "sns:Publish"],
    "Resource": "*"
  }]
}
```

Para producción restringe recursos a topics concretos cuando sea posible. SMS puede requerir configuración/registros por país y genera costos.

## Pruebas

```bash
python test_connection.py
python validate_local.py
```

`validate_local.py` no publica ni envía SMS reales salvo que definas flags explícitos:

```bash
export RUVIC_AWS_SNS_RUN_PUBLISH_TESTS=true
export RUVIC_AWS_SNS_TEST_TOPIC_ARN="arn:aws:sns:..."
python validate_local.py
```

Para SMS real:

```bash
export RUVIC_AWS_SNS_ALLOW_SMS=true
export RUVIC_AWS_SNS_RUN_SMS_TESTS=true
export RUVIC_AWS_SNS_TEST_PHONE_NUMBER="+573001234567"
python validate_local.py
```

## Seguridad

- No uses credenciales root.
- Nunca subas access keys al repositorio.
- SMS está bloqueado por defecto por costo/impacto.
- Confirma con el usuario antes de publicar en topics que disparen notificaciones reales.
