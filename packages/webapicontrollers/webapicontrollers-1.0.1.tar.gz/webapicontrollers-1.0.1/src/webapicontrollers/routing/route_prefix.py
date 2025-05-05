def RoutePrefix(prefix: str):
    def decorator(cls):
        cls._route_prefix = prefix
        return cls
    return decorator