from typing import Dict, Any, Optional
import hashlib
import jwt
import datetime
from ..models.user import UserModel
from modular_system.database.connection import session_scope

class AuthService:
    def __init__(self, module):
        self.module = module
        auth_cfg = self.module.config.get('auth', {})
        self.secret_key = auth_cfg.get('jwt_secret', 'your-secret-key')
        self.access_expiry = auth_cfg.get('access_token_expiry', 3600)
        self.refresh_expiry = auth_cfg.get('refresh_token_expiry', 604800)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_token(self, user_id: int, is_refresh: bool = False) -> str:
        expiry = self.refresh_expiry if is_refresh else self.access_expiry
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry),
            'iat': datetime.datetime.utcnow(),
            'type': 'refresh' if is_refresh else 'access'
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token: str, expected_type: str = 'access') -> Optional[int]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            if payload.get('type') != expected_type:
                return None
            return payload['user_id']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        user_id = self.verify_token(refresh_token, expected_type='refresh')
        if user_id:
            return {
                'access_token': self.create_token(user_id, is_refresh=False),
                'refresh_token': self.create_token(user_id, is_refresh=True)
            }
        return None

    def register(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if 'password' in user_data:
            user_data['password'] = self._hash_password(user_data['password'])
        
        user = UserModel.from_dict(user_data)
        with session_scope() as s:
            s.add(user)
            s.flush()
            s.refresh(user)
            user_dict = user.to_dict()
            user_dict['access_token'] = self.create_token(user.id, is_refresh=False)
            user_dict['refresh_token'] = self.create_token(user.id, is_refresh=True)
            return user_dict

    def login(self, username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
        hashed_pw = self._hash_password(password)
        with session_scope(False) as s:
            user = s.query(UserModel).filter(
                (UserModel.username == username_or_email) | (UserModel.email == username_or_email)
            ).first()
            
            if user and user.password == hashed_pw:
                user_dict = user.to_dict()
                user_dict['access_token'] = self.create_token(user.id, is_refresh=False)
                user_dict['refresh_token'] = self.create_token(user.id, is_refresh=True)
                return user_dict
        return None
