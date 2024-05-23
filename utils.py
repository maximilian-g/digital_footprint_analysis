
def extract_safely(obj, key, default_value=None):
    return obj[key] if key in obj else default_value