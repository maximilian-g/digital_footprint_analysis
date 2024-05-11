
def extract_safely(obj, key):
    return obj[key] if key in obj else None