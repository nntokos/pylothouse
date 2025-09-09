_REGISTRY = {}

def register(name):
    def deco(cls):
        _REGISTRY[name] = cls
        return cls
    return deco

def make(name, **kwargs):
    if name not in _REGISTRY:
        raise KeyError(f"Plot type '{name}' is not registered.")
    return _REGISTRY[name](**kwargs)
