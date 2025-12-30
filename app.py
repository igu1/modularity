import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from modular_system import ModularSystem
from config.settings import get_config

def main():
    cfg = get_config()
    ms = ModularSystem(asdict(cfg))
    for m in ['base', 'support']:
        if ms.load_module(m): print(f"✓ {m}")
        else: print(f"✗ {m}"); sys.exit(1)
    
    print(f"\nServing on {cfg.svr.host}:{cfg.svr.port}")
    ms.run(host=cfg.svr.host, port=cfg.svr.port)

if __name__ == "__main__":
    from dataclasses import asdict
    main()
