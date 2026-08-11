"""Prueba de conexión estándar del conector AWS SNS."""
from __future__ import annotations

def test_connection() -> tuple[bool, str]:
    """Prueba credenciales y permisos básicos listando topics SNS."""
    try:
        from ruvic_aws_sns_connector import AwsSnsAuthError, AwsSnsClient, AwsSnsConfigError, AwsSnsDataError, AwsSnsNetworkError, AwsSnsSecurityError
    except ImportError:
        return False, "La librería ruvic-aws-sns-connector no está instalada. Instala con: pip install git+https://github.com/montealegre777/conector-aws-sns.git#subdirectory=lib"
    try:
        client = AwsSnsClient(); client.ping()
    except ValueError as exc:
        return False, str(exc)
    except AwsSnsConfigError as exc:
        return False, f"Configuración inválida: {exc}"
    except AwsSnsAuthError as exc:
        return False, f"Autenticación o permisos AWS inválidos: {exc}"
    except AwsSnsNetworkError as exc:
        return False, f"Error de red hacia AWS SNS: {exc}"
    except AwsSnsSecurityError as exc:
        return False, f"Bloqueo de seguridad: {exc}"
    except AwsSnsDataError as exc:
        return False, f"AWS SNS rechazó la solicitud: {exc}"
    except Exception as exc:
        return False, f"Error inesperado probando AWS SNS: {exc}"
    return True, f"Conexión exitosa a AWS SNS en región {client.config.region}."

if __name__ == "__main__":
    ok, message = test_connection(); print(f"{'OK' if ok else 'FALLO'}: {message}"); raise SystemExit(0 if ok else 1)
