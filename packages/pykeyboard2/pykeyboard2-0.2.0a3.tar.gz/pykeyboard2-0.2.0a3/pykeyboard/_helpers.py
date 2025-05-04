def require_module(module, error_message: str):
    def decorator(cls):
        if module is None:

            class Fallback:
                def __init__(self, *args, **kwargs):
                    raise ImportError(error_message)

            return Fallback
        return type(cls.__name__, (module,), dict(cls.__dict__))

    return decorator
