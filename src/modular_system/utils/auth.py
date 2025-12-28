import hashlib, secrets, random, string, base64
from typing import Optional, Tuple, List
from urllib.parse import parse_qs

class Auth:
    @staticmethod
    def gen_token(n: int = 32) -> str: return secrets.token_urlsafe(n)
    @staticmethod
    def hash_pw(pw: str, salt: str = None) -> Tuple[str, str]:
        salt = salt or secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000).hex(), salt
    @staticmethod
    def verify_pw(pw: str, h: str, s: str) -> bool: return secrets.compare_digest(Auth.hash_pw(pw, s)[0], h)
    @staticmethod
    def get_bearer(env: dict) -> Optional[str]:
        h = env.get('HTTP_AUTHORIZATION', '')
        return h[7:] if h.startswith('Bearer ') else None
    @staticmethod
    def get_api_key(env: dict) -> Optional[str]:
        return env.get('HTTP_X_API_KEY') or parse_qs(env.get('QUERY_STRING', '')).get('api_key', [None])[0]
    @staticmethod
    def is_strong(pw: str) -> bool:
        return len(pw) >= 8 and any(c.isupper() for c in pw) and any(c.islower() for c in pw) and any(c.isdigit() for c in pw)
    @staticmethod
    def suggest_pw(n: int = 3) -> List[str]:
        res = []
        for _ in range(n):
            p = [random.choice(string.ascii_uppercase), random.choice(string.ascii_lowercase), random.choice(string.digits), random.choice('!@#$%^&*')]
            chars = string.ascii_letters + string.digits + '!@#$%^&*'
            p += [random.choice(chars) for _ in range(random.randint(8, 16) - 4)]
            random.shuffle(p)
            res.append(''.join(p))
        return res
    @staticmethod
    def crypt(data: str, key: str, enc: bool = True) -> str:
        from cryptography.fernet import Fernet
        f = Fernet(base64.urlsafe_b64encode(key.encode()[:32].ljust(32, b'0')))
        return f.encrypt(data.encode()).decode() if enc else f.decrypt(data.encode()).decode()

class Permissions:
    @staticmethod
    def check(user_perms: list, req: str) -> bool: return req in user_perms
    @staticmethod
    def check_any(user_perms: list, reqs: list) -> bool: return any(p in user_perms for p in reqs)
    @staticmethod
    def is_admin(user_perms: list) -> bool: return any(p in user_perms for p in ['admin', 'super_admin'])

class RateLimiter:
    def __init__(self, limit: int = 100, window: int = 3600):
        self.limit, self.window, self.reqs = limit, window, {}
    def is_allowed(self, uid: str) -> bool:
        import time
        now = time.time()
        self.reqs[uid] = [t for t in self.reqs.get(uid, []) if t > now - self.window]
        if len(self.reqs[uid]) < self.limit:
            self.reqs[uid].append(now)
            return True
        return False
