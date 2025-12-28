import re
from typing import Any, Dict, List, Tuple, Optional

class Validate:
    @staticmethod
    def email(e: str) -> bool: return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', e)) if e else False
    @staticmethod
    def url(u: str) -> bool: return bool(re.match(r'^https?://\S+$', u)) if u else False
    @staticmethod
    def req(data: Dict, fields: List[str]) -> Tuple[bool, List[str]]:
        missing = [f for f in fields if f not in data or not str(data[f]).strip()]
        return not missing, missing
    @staticmethod
    def types(data: Dict, types: Dict[str, type]) -> Tuple[bool, List[str]]:
        invalid = [f for f, t in types.items() if f in data and not isinstance(data[f], t)]
        return not invalid, invalid

class Validator:
    def __init__(self): self.rules = {}
    def add(self, field, func, msg):
        self.rules.setdefault(field, []).append((func, msg))
    def validate(self, data: Dict) -> Tuple[bool, Dict[str, List[str]]]:
        errs = {}
        for f, rules in self.rules.items():
            for func, msg in rules:
                if not func(data.get(f)): errs.setdefault(f, []).append(msg)
        return not errs, errs
