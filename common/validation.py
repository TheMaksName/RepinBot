import re

def validate_fio(fio: str) -> bool:
    parts = fio.split()
    if len(parts) != 3:
        return False

    for part in parts:
        if not part.istitle():
            return False

    return True


def validate_phone_number(phone: str) -> bool:
    # Проверка на формат +7XXXXXXXXXX или 8XXXXXXXXXX
    pattern = r"^(\+7|8)\d{10}$"
    return bool(re.match(pattern, phone))