def normalize_scan_type(raw_scan_type: str) -> str:
    """
    Normalizes scan type aliases to standard forms:
    XRAY, X-RAY, X_RAY, xray -> X-RAY
    MRI SCAN, MRISCAN, MRI -> MRI
    CT SCAN, CTSCAN, CT -> CT
    """
    if not raw_scan_type:
        return "X-RAY"
        
    cleaned = raw_scan_type.strip().upper().replace(" ", "").replace("_", "").replace("-", "")
    
    if "XRAY" in cleaned:
        return "X-RAY"
    elif "MRI" in cleaned:
        return "MRI"
    elif "CT" in cleaned:
        return "CT"
    elif "ULTRASOUND" in cleaned:
        return "ULTRASOUND"
    else:
        return cleaned
