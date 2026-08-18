import re

from django.core.exceptions import ValidationError


def normalize_rut(value):
    clean = re.sub(r"[^0-9kK]", "", value or "").upper()
    if len(clean) < 2 or not clean[:-1].isdigit():
        return clean
    return f"{int(clean[:-1])}-{clean[-1]}"


def validate_rut(value):
    clean = re.sub(r"[^0-9kK]", "", value or "").upper()
    if len(clean) < 2 or not clean[:-1].isdigit():
        raise ValidationError("Ingrese un RUT chileno válido, por ejemplo 12.345.678-5.")

    body = clean[:-1]
    supplied = clean[-1]
    factor = 2
    total = 0
    for digit in reversed(body):
        total += int(digit) * factor
        factor = 2 if factor == 7 else factor + 1

    result = 11 - (total % 11)
    expected = "0" if result == 11 else "K" if result == 10 else str(result)
    if supplied != expected:
        raise ValidationError("El dígito verificador del RUT no es correcto.")
