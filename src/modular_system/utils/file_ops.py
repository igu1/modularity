import os, shutil, hashlib, mimetypes
from typing import Optional, List, Dict, Any, Union

class Files:
    @staticmethod
    def ensure_dir(path: str): os.makedirs(path, exist_ok=True)
    @staticmethod
    def exists(path: str) -> bool: return os.path.exists(path)
    @staticmethod
    def size(path: str) -> int: return os.path.getsize(path) if os.path.exists(path) else 0
    @staticmethod
    def ext(path: str) -> str: return os.path.splitext(path)[1].lower()
    @staticmethod
    def mime(path: str) -> str: return mimetypes.guess_type(path)[0] or 'application/octet-stream'
    @staticmethod
    def copy(src: str, dst: str):
        Files.ensure_dir(os.path.dirname(dst))
        shutil.copy2(src, dst)
    @staticmethod
    def move(src: str, dst: str):
        Files.ensure_dir(os.path.dirname(dst))
        shutil.move(src, dst)
    @staticmethod
    def delete(path: str):
        if os.path.isfile(path): os.remove(path)
        elif os.path.isdir(path): shutil.rmtree(path)
    @staticmethod
    def hash(path: str, alg: str = 'sha256') -> Optional[str]:
        try:
            h = hashlib.new(alg)
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""): h.update(chunk)
            return h.hexdigest()
        except: return None
    @staticmethod
    def read(path: str, bin: bool = False) -> Any:
        try:
            with open(path, 'rb' if bin else 'r') as f: return f.read()
        except: return None
    @staticmethod
    def write(path: str, data: Any, bin: bool = False):
        Files.ensure_dir(os.path.dirname(path))
        with open(path, 'wb' if bin else 'w') as f: f.write(data)
    @staticmethod
    def list(path: str, pattern: str = "*", rec: bool = False) -> List[str]:
        import glob
        return glob.glob(os.path.join(path, "**" if rec else "", pattern), recursive=rec)
