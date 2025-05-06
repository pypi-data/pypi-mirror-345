

def build(params: dict) -> str:
    """
    Build an HTTP Query parameters string from dictionary.
    :param params: dictionary with all parameters key-value pairs
    :return: a query string
    """
    return f"{'&'.join([f'{str(key)}={str(val)}' for key, val in params.items() if val])}"
