import os, importlib.util
from typing import Dict, Any, List, Optional
from .patch_types import Patch

class PatchEngine:
    def __init__(self):
        self.patches: Dict[str, List[Patch]] = {}
        self.logger: Optional[Any] = None
        self.applied: List[str] = []

    def set_logger(self, logger): self.logger = logger

    def load_patches_from_directory(self, directory: str):
        if not os.path.exists(directory): return
        for f in os.listdir(directory):
            if f.endswith('.py') and not f.startswith('__') and f not in ['patch_engine.py', 'patch_types.py']:
                try:
                    name = f[:-3]
                    spec = importlib.util.spec_from_file_location(name, os.path.join(directory, f))
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, 'get_patches'):
                        self.patches[name] = mod.get_patches()
                except Exception as e:
                    if self.logger: self.logger.log("extensions", f"Load fail {f}: {e}", "error")

    def apply_patches_to_module(self, mod_name: str, inst: Any, env: Any) -> int:
        count = 0
        for p_name, patches in self.patches.items():
            for p in patches:
                if not getattr(p, 'target', None) or p.target in [mod_name, '*']:
                    try:
                        p.apply(inst, env)
                        count += 1
                        self.applied.append(f"{p_name}.{p.name}")
                    except Exception as e:
                        if self.logger: self.logger.log("extensions", f"Patch fail {p.name}: {e}", "error")
        return count

    def get_statistics(self) -> Dict[str, Any]:
        return {'total': sum(len(v) for v in self.patches.values()), 'files': len(self.patches), 'applied_count': len(self.applied), 'applied': self.applied}
