import re


def parse_phone(raw):
    """Clean and validate a phone number.

    Returns the digits-only phone string if valid, otherwise None.
    Allowed input may include digits, spaces, parentheses, hyphens, dots, and a leading plus.
    Alphabetic characters or other symbols are rejected.
    """
    if raw is None:
        return None

    phone = str(raw).strip()
    if not phone:
        return None

    # Reject alphabetic characters explicitly.
    if re.search(r'[A-Za-z]', phone):
        return None

    # Allow digits and common phone formatting characters only.
    if not re.match(r'^[\d\+\-\.\(\)\s]+$', phone):
        return None

    digits = re.sub(r'\D', '', phone)
    if len(digits) < 10 or len(digits) > 15:
        return None

    return digits
