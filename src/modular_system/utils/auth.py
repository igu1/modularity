import hashlib
import secrets
from typing import Optional, Tuple
from urllib.parse import parse_qs
from ..logging.logger import CoreLogger
logger = CoreLogger()
class AuthHelpers:
    @staticmethod
    def generate_token(length: int = 32) -> str:
        return secrets.token_urlsafe(length)
    @staticmethod
    def generate_api_key(length: int = 40) -> str:
        return secrets.token_urlsafe(length)
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        if salt is None:
            salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000                        
        )
        return password_hash.hex(), salt
    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        hash_calc, _ = AuthHelpers.hash_password(password, salt)
        return secrets.compare_digest(hash_calc, password_hash)
    @staticmethod
    def get_bearer_token(environ: dict) -> Optional[str]:
        auth_header = environ.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None
    @staticmethod
    def get_api_key(environ: dict) -> Optional[str]:
        api_key = environ.get('HTTP_X_API_KEY')
        if api_key:
            return api_key
        query_string = environ.get('QUERY_STRING', '')
        params = parse_qs(query_string)
        if 'api_key' in params:
            return params['api_key'][0]
        return None
    @staticmethod
    def generate_session_token() -> str:
        return secrets.token_urlsafe(32)
    @staticmethod
    def hash_data(data: str, salt: Optional[str] = None) -> Tuple[str, str]:
        if salt is None:
            salt = secrets.token_hex(16)
        data_hash = hashlib.sha256(
            (data + salt).encode('utf-8')
        ).hexdigest()
        return data_hash, salt
    @staticmethod
    def verify_data(data: str, data_hash: str, salt: str) -> bool:
        hash_calc, _ = AuthHelpers.hash_data(data, salt)
        return secrets.compare_digest(hash_calc, data_hash)
    @staticmethod
    def is_strong_password(password: str) -> bool:
        if len(password) < 8:
            return False
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@
        return has_upper and has_lower and has_digit and has_special
    @staticmethod
    def generate_password_suggestions(count: int = 3) -> list:
        import random
        import string
        suggestions = []
        for _ in range(count):
            password = [
                random.choice(string.ascii_uppercase),
                random.choice(string.ascii_lowercase),
                random.choice(string.digits),
                random.choice('!@
            ]
            remaining_length = random.randint(8, 16) - 4
            all_chars = string.ascii_letters + string.digits + '!@
            password.extend(random.choice(all_chars) for _ in range(remaining_length))
            random.shuffle(password)
            suggestions.append(''.join(password))
        return suggestions
    @staticmethod
    def create_csrf_token() -> str:
        return secrets.token_urlsafe(32)
    @staticmethod
    def verify_csrf_token(token: str, expected_token: str) -> bool:
        return secrets.compare_digest(token, expected_token)
    @staticmethod
    def encrypt_sensitive_data(data: str, key: str) -> str:
        from cryptography.fernet import Fernet
        import base64
        key_bytes = base64.urlsafe_b64encode(key.encode()[:32].ljust(32, b'0'))
        f = Fernet(key_bytes)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data.decode()
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str, key: str) -> str:
        from cryptography.fernet import Fernet
        import base64
        key_bytes = base64.urlsafe_b64encode(key.encode()[:32].ljust(32, b'0'))
        f = Fernet(key_bytes)
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
class PermissionChecker:
    def __init__(self, permissions: list = None):
        self.permissions = permissions or []
    def has_permission(self, user_permissions: list, required_permission: str) -> bool:
        return required_permission in user_permissions
    def has_any_permission(self, user_permissions: list, required_permissions: list) -> bool:
        return any(perm in user_permissions for perm in required_permissions)
    def has_all_permissions(self, user_permissions: list, required_permissions: list) -> bool:
        return all(perm in user_permissions for perm in required_permissions)
    def is_admin(self, user_permissions: list) -> bool:
        return self.has_permission(user_permissions, 'admin') or self.has_permission(user_permissions, 'super_admin')
class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    def is_allowed(self, identifier: str) -> bool:
        import time
        now = time.time()
        window_start = now - self.window_seconds
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        return False
    def get_remaining_requests(self, identifier: str) -> int:
        import time
        now = time.time()
        window_start = now - self.window_seconds
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            return max(0, self.max_requests - len(self.requests[identifier]))
        return self.max_requests
