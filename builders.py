def time_str_to_seconds(t: str) -> float:
    """
    Converts 'HH:MM:SS.mmm' or 'MM:SS' or 'SS.mmm' → seconds
    Strips brackets and whitespace automatically.
    """
    t = t.strip().strip("[]")  
    parts = t.split(":")
    parts = [float(p) for p in parts]
    
    if len(parts) == 3:
        h, m, s = parts
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = parts
        return m * 60 + s
    else:
        return parts[0]

    

def time_to_frame(time_str: str, fps: float) -> int:
    return int(time_str_to_seconds(time_str) * fps)

def clean_field(s: str) -> str:
    return s.strip().strip("[]").strip('"').strip("'")

def parse_list_field(s: str):
    cleaned = clean_field(s)
    if not cleaned:
        return []
    # split by comma, remove extra spaces
    return [item.strip() for item in cleaned.split(",")]
