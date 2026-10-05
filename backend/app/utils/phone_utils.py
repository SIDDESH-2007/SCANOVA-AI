import re
from typing import Optional

def normalize_phone_number(phone_str: str, default_country_code: str = "+91") -> Optional[str]:
    """
    Normalizes entered phone numbers into E.164 format (+91XXXXXXXXXX).
    Examples:
      '9876543210'       -> '+919876543210'
      '+91 9876543210'   -> '+919876543210'
      '+91-9876543210'   -> '+919876543210'
      '09876543210'      -> '+919876543210'
      '+919876543210'    -> '+919876543210'
    """
    if not phone_str:
        return None
    
    # Strip whitespace, hyphens, dots, parentheses, brackets
    cleaned = re.sub(r'[\s\-\(\)\[\]\.]', '', str(phone_str).strip())
    if not cleaned:
        return None

    if cleaned.startswith("+"):
        digits_only = cleaned[1:]
        if not digits_only.isdigit() or len(digits_only) < 10 or len(digits_only) > 15:
            return None
        return cleaned

    if not cleaned.isdigit():
        return None

    # If 10 digits, prefix default_country_code (+91)
    if len(cleaned) == 10:
        return f"{default_country_code}{cleaned}"

    # If 11 digits starting with leading zero e.g. 09876543210
    if len(cleaned) == 11 and cleaned.startswith("0"):
        return f"{default_country_code}{cleaned[1:]}"

    # If 12 digits starting with 91 e.g. 919876543210
    if len(cleaned) == 12 and cleaned.startswith("91"):
        return f"+{cleaned}"

    if 10 <= len(cleaned) <= 15:
        return f"+{cleaned}"

    return None

def normalize_patient_id(patient_id_str: str) -> Optional[str]:
    """
    Normalizes patient ID into canonical format (trimmed, uppercase).
    Examples:
      'pat-001'   -> 'PAT-001'
      'PAT-001'   -> 'PAT-001'
      ' PAT-001 ' -> 'PAT-001'
    """
    if not patient_id_str:
        return None
    cleaned = str(patient_id_str).strip().upper()
    return cleaned if cleaned else None
