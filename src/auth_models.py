"""
Authentication models for Healthcare Planning Assistant
User management and session handling
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import json
import os

@dataclass
class User:
    """User model for authentication"""
    id: str
    username: str
    email: str
    password_hash: str
    full_name: str
    role: str = "user"  # user, admin
    created_at: datetime = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary (excluding sensitive data unless specified)"""
        user_dict = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active
        }
        if include_sensitive:
            user_dict["password_hash"] = self.password_hash
        return user_dict
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return self.password_hash == self.hash_password(password)

@dataclass
class Session:
    """Session model for user authentication"""
    session_id: str
    user_id: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=24)  # 24-hour sessions
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active
        }

class AuthManager:
    """Authentication manager for user and session management"""
    
    def __init__(self, data_file: Optional[str] = None):
        if data_file is None:
            # Default to <project_root>/data/users.json
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_file = os.path.join(project_root, "data", "users.json")
        else:
            self.data_file = data_file
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self._load_data()
    
    def _load_data(self):
        """Load users and sessions from file"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load users
                    for user_id, user_data in data.get('users', {}).items():
                        user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                        if user_data.get('last_login'):
                            user_data['last_login'] = datetime.fromisoformat(user_data['last_login'])
                        if 'password_hash' not in user_data:
                            user_data['password_hash'] = User.hash_password("admin123")
                        self.users[user_id] = User(**user_data)
                    
                    # Load sessions
                    for session_id, session_data in data.get('sessions', {}).items():
                        session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
                        session_data['expires_at'] = datetime.fromisoformat(session_data['expires_at'])
                        self.sessions[session_id] = Session(**session_data)
        except Exception as e:
            print(f"Error loading auth data: {e}")
    
    def _save_data(self):
        """Save users and sessions to file"""
        try:
            data = {
                'users': {user_id: user.to_dict(include_sensitive=True) for user_id, user in self.users.items()},
                'sessions': {session_id: session.to_dict() for session_id, session in self.sessions.items()}
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving auth data: {e}")
    
    def create_user(self, username: str, email: str, password: str, full_name: str, role: str = "user") -> Optional[User]:
        """Create a new user"""
        # Check if username or email already exists
        for user in self.users.values():
            if user.username == username or user.email == email:
                return None
        
        # Create new user
        user_id = secrets.token_hex(16)
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=User.hash_password(password),
            full_name=full_name,
            role=role
        )
        
        self.users[user_id] = user
        self._save_data()
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        for user in self.users.values():
            if user.username == username and user.verify_password(password):
                # Update last login
                user.last_login = datetime.now()
                self._save_data()
                return user
        return None
    
    def create_session(self, user: User) -> Session:
        """Create a new session for user"""
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        
        session_id = secrets.token_hex(32)
        session = Session(
            session_id=session_id,
            user_id=user.id
        )
        
        self.sessions[session_id] = session
        self._save_data()
        return session
    
    def get_user_by_session(self, session_id: str) -> Optional[User]:
        """Get user by session ID"""
        session = self.sessions.get(session_id)
        if session and not session.is_expired():
            return self.users.get(session.user_id)
        
        # Remove expired session
        if session and session.is_expired():
            del self.sessions[session_id]
            self._save_data()
        
        return None
    
    def logout(self, session_id: str):
        """Logout user by removing session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_data()
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user information"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self._save_data()
        return True
