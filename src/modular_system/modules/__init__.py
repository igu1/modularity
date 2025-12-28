import os, importlib
modules = {}

def discover():
    d = os.path.dirname(__file__)
    res = {}
    for item in os.listdir(d):
        if os.path.isdir(os.path.join(d, item)) and not item.startswith('__'):
            try:
                mod = importlib.import_module(f'.{item}', 'modular_system.modules')
                for a in dir(mod):
                    attr = getattr(mod, a)
                    if isinstance(attr, type) and a.endswith('Module'):
                        res[item] = attr; break
            except Exception as e: print(f"Load fail {item}: {e}")
    return res

modules = discover()
