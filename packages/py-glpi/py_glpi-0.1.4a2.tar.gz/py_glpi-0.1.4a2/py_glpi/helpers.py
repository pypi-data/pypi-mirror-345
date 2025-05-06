def get_item_url(base_url: str, item_type: str):
    return f"{base_url}/{item_type}/"
    
def parse_kwargs(kwargs: dict) -> dict:
    kwargs = {k: v for k, v in kwargs.items() if not (isinstance(v, bool) and not v)}
    return kwargs