import re

def normalize_scan_type(value: str) -> str:
    """
    Safely accept various scan type inputs and normalize them to:
    - X-RAY
    - CT
    - MRI
    - ULTRASOUND
    """
    if not value or not isinstance(value, str):
        return ""
        
    # Remove spaces, underscores, and hyphens, convert to upper
    normalized = re.sub(r'[\s_\-]', '', value).upper()
    
    if normalized == 'XRAY':
        return 'X-RAY'
    elif normalized in ['CT', 'CTSCAN']:
        return 'CT'
    elif normalized in ['MRI', 'MRISCAN']:
        return 'MRI'
    elif normalized in ['ULTRASOUND', 'US', 'ULTRASOUNDSCAN']:
        return 'ULTRASOUND'
        
    # Default uppercase trimmed value
    return value.strip().upper()

