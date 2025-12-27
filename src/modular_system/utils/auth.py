"""Authentication and authorization utilities."""

import hashlib
import secrets
from typing import Optional, Tuple
from urllib.parse import parse_qs
from ..logging.logger import CoreLogger

logger = CoreLogger()


class AuthHelpers:
    """Authentication and authorization utility functions."""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate a secure random token.
        
        Args:
            length: Length of the token to generate
            
        Returns:
            Secure random token string
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_api_key(length: int = 40) -> str:
        """
        Generate an API key.
        
        Args:
            length: Length of the API key
            
        Returns:
            API key string
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash a password with salt using PBKDF2.
        
        Args:
            password: Password to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (password_hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Number of iterations
        )
        
        return password_hash.hex(), salt
    
    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Password to verify
            password_hash: Hash to verify against
            salt: Salt used for hashing
            
        Returns:
            True if password matches, False otherwise
        """
        hash_calc, _ = AuthHelpers.hash_password(password, salt)
        return secrets.compare_digest(hash_calc, password_hash)
    
    @staticmethod
    def get_bearer_token(environ: dict) -> Optional[str]:
        """
        Extract Bearer token from Authorization header.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            Bearer token string or None if not found
        """
        auth_header = environ.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None
    
    @staticmethod
    def get_api_key(environ: dict) -> Optional[str]:
        """
        Extract API key from headers or query parameters.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            API key string or None if not found
        """
        # Try header first
        api_key = environ.get('HTTP_X_API_KEY')
        if api_key:
            return api_key
        
        # Try query parameter
        query_string = environ.get('QUERY_STRING', '')
        params = parse_qs(query_string)
        if 'api_key' in params:
            return params['api_key'][0]
        
        return None
    
    @staticmethod
    def generate_session_token() -> str:
        """
        Generate a secure session token.
        
        Returns:
            Session token string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_data(data: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash arbitrary data with salt.
        
        Args:
            data: Data to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (data_hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        data_hash = hashlib.sha256(
            (data + salt).encode('utf-8')
        ).hexdigest()
        
        return data_hash, salt
    
    @staticmethod
    def verify_data(data: str, data_hash: str, salt: str) -> bool:
        """
        Verify data against its hash.
        
        Args:
            data: Data to verify
            data_hash: Hash to verify against
            salt: Salt used for hashing
            
        Returns:
            True if data matches, False otherwise
        """
        hash_calc, _ = AuthHelpers.hash_data(data, salt)
        return secrets.compare_digest(hash_calc, data_hash)
    
    @staticmethod
    def is_strong_password(password: str) -> bool:
        """
        Check if a password meets strength requirements.
        
        Args:
            password: Password to check
            
        Returns:
            True if password is strong enough
        """
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    @staticmethod
    def generate_password_suggestions(count: int = 3) -> list:
        """
        Generate strong password suggestions.
        
        Args:
            count: Number of suggestions to generate
            
        Returns:
            List of password suggestions
        """
        import random
        import string
        
        suggestions = []
        
        for _ in range(count):
            # Generate password with at least one of each required type
            password = [
                random.choice(string.ascii_uppercase),
                random.choice(string.ascii_lowercase),
                random.choice(string.digits),
                random.choice('!@#$%^&*()_+-=[]{}|;:,.<>?')
            ]
            
            # Fill the rest with random characters
            remaining_length = random.randint(8, 16) - 4
            all_chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
            password.extend(random.choice(all_chars) for _ in range(remaining_length))
            
            # Shuffle the password
            random.shuffle(password)
            suggestions.append(''.join(password))
        
        return suggestions
    
    @staticmethod
    def create_csrf_token() -> str:
        """
        Create a CSRF token.
        
        Returns:
            CSRF token string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token: str, expected_token: str) -> bool:
        """
        Verify a CSRF token.
        
        Args:
            token: Token to verify
            expected_token: Expected token value
            
        Returns:
            True if tokens match
        """
        return secrets.compare_digest(token, expected_token)
    
    @staticmethod
    def encrypt_sensitive_data(data: str, key: str) -> str:
        """
        Simple encryption for sensitive data (note: use proper encryption in production).
        
        Args:
            data: Data to encrypt
            key: Encryption key
            
        Returns:
            Encrypted data
        """
        from cryptography.fernet import Fernet
        import base64
        
        # In production, use proper key management
        key_bytes = base64.urlsafe_b64encode(key.encode()[:32].ljust(32, b'0'))
        f = Fernet(key_bytes)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data.decode()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str, key: str) -> str:
        """
        Simple decryption for sensitive data (note: use proper encryption in production).
        
        Args:
            encrypted_data: Data to decrypt
            key: Decryption key
            
        Returns:
            Decrypted data
        """
        from cryptography.fernet import Fernet
        import base64
        
        key_bytes = base64.urlsafe_b64encode(key.encode()[:32].ljust(32, b'0'))
        f = Fernet(key_bytes)
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()


class PermissionChecker:
    """Utility class for checking permissions."""
    
    def __init__(self, permissions: list = None):
        """
        Initialize the permission checker.
        
        Args:
            permissions: List of available permissions
        """
        self.permissions = permissions or []
    
    def has_permission(self, user_permissions: list, required_permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user_permissions: List of user's permissions
            required_permission: Permission to check
            
        Returns:
            True if user has permission
        """
        return required_permission in user_permissions
    
    def has_any_permission(self, user_permissions: list, required_permissions: list) -> bool:
        """
        Check if user has any of the required permissions.
        
        Args:
            user_permissions: List of user's permissions
            required_permissions: List of permissions to check
            
        Returns:
            True if user has any of the permissions
        """
        return any(perm in user_permissions for perm in required_permissions)
    
    def has_all_permissions(self, user_permissions: list, required_permissions: list) -> bool:
        """
        Check if user has all required permissions.
        
        Args:
            user_permissions: List of user's permissions
            required_permissions: List of permissions to check
            
        Returns:
            True if user has all permissions
        """
        return all(perm in user_permissions for perm in required_permissions)
    
    def is_admin(self, user_permissions: list) -> bool:
        """
        Check if user has admin privileges.
        
        Args:
            user_permissions: List of user's permissions
            
        Returns:
            True if user is admin
        """
        return self.has_permission(user_permissions, 'admin') or self.has_permission(user_permissions, 'super_admin')


class RateLimiter:
    """Simple rate limiter for API endpoints."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for identifier.
        
        Args:
            identifier: Unique identifier (IP address, user ID, etc.)
            
        Returns:
            True if request is allowed
        """
        import time
        
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, identifier: str) -> int:
        """
        Get remaining requests for identifier.
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Number of remaining requests
        """
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
