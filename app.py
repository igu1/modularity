import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from modular_system import ModularSystem
from config.settings import get_config

def main():
    cfg = get_config()
    sys = ModularSystem(asdict(cfg))
    for m in ['base']:
        if sys.load_module(m): print(f"✓ {m}")
        else: print(f"✗ {m}"); sys.exit(1)
    
    print(f"\nServing on {cfg.svr.host}:{cfg.svr.port}")
    sys.run(host=cfg.svr.host, port=cfg.svr.port)

if __name__ == "__main__":
    from dataclasses import asdict
    main()
