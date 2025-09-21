"""Data encryption and protection utilities."""

import os
import base64
import secrets
from typing import Optional, Dict, Any, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EncryptionConfig:
    """Encryption configuration constants."""
    
    # AES encryption
    AES_KEY_SIZE = 32  # 256 bits
    AES_IV_SIZE = 16   # 128 bits
    
    # PBKDF2 parameters
    PBKDF2_ITERATIONS = 100000
    SALT_SIZE = 32
    
    # RSA parameters
    RSA_KEY_SIZE = 2048
    
    # Token expiration
    TOKEN_EXPIRY_HOURS = 24


class DataEncryption:
    """Data encryption utilities for sensitive information."""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize encryption with master key."""
        if master_key:
            self.master_key = master_key.encode()
        else:
            # Generate or load master key from environment
            self.master_key = self._get_or_generate_master_key()
    
    def _get_or_generate_master_key(self) -> bytes:
        """Get master key from environment or generate new one."""
        master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        if master_key:
            return base64.b64decode(master_key)
        
        # Generate new master key
        key = secrets.token_bytes(EncryptionConfig.AES_KEY_SIZE)
        encoded_key = base64.b64encode(key).decode()
        
        logger.warning(
            f"Generated new master key. Set ENCRYPTION_MASTER_KEY={encoded_key} "
            "in your environment variables for production use."
        )
        
        return key
    
    def derive_key(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Derive encryption key from password using PBKDF2."""
        if salt is None:
            salt = secrets.token_bytes(EncryptionConfig.SALT_SIZE)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=EncryptionConfig.AES_KEY_SIZE,
            salt=salt,
            iterations=EncryptionConfig.PBKDF2_ITERATIONS,
        )
        
        key = kdf.derive(password.encode())
        return key, salt
    
    def encrypt_data(self, data: str, key: Optional[bytes] = None) -> Dict[str, str]:
        """Encrypt data using AES-256-GCM."""
        if key is None:
            key = self.master_key
        
        # Generate random IV
        iv = secrets.token_bytes(EncryptionConfig.AES_IV_SIZE)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv)
        )
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'iv': base64.b64encode(iv).decode(),
            'tag': base64.b64encode(encryptor.tag).decode(),
            'algorithm': 'AES-256-GCM'
        }
    
    def decrypt_data(self, encrypted_data: Dict[str, str], key: Optional[bytes] = None) -> str:
        """Decrypt data using AES-256-GCM."""
        if key is None:
            key = self.master_key
        
        try:
            # Decode components
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            iv = base64.b64decode(encrypted_data['iv'])
            tag = base64.b64decode(encrypted_data['tag'])
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag)
            )
            decryptor = cipher.decryptor()
            
            # Decrypt data
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext.decode()
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Failed to decrypt data")
    
    def encrypt_file_content(self, file_content: bytes, key: Optional[bytes] = None) -> Dict[str, str]:
        """Encrypt file content."""
        if key is None:
            key = self.master_key
        
        # Convert bytes to base64 string for encryption
        content_b64 = base64.b64encode(file_content).decode()
        return self.encrypt_data(content_b64, key)
    
    def decrypt_file_content(self, encrypted_data: Dict[str, str], key: Optional[bytes] = None) -> bytes:
        """Decrypt file content."""
        if key is None:
            key = self.master_key
        
        # Decrypt to base64 string
        content_b64 = self.decrypt_data(encrypted_data, key)
        # Decode base64 to bytes
        return base64.b64decode(content_b64)


class TokenManager:
    """Secure token management for sessions and API keys."""
    
    def __init__(self, secret_key: str):
        """Initialize token manager with secret key."""
        self.fernet = Fernet(base64.urlsafe_b64encode(secret_key[:32].encode().ljust(32, b'0')))
    
    def create_token(self, data: Dict[str, Any], expires_hours: int = EncryptionConfig.TOKEN_EXPIRY_HOURS) -> str:
        """Create encrypted token with expiration."""
        token_data = {
            'data': data,
            'expires': (datetime.utcnow() + timedelta(hours=expires_hours)).isoformat(),
            'created': datetime.utcnow().isoformat()
        }
        
        token_json = json.dumps(token_data)
        encrypted_token = self.fernet.encrypt(token_json.encode())
        return base64.urlsafe_b64encode(encrypted_token).decode()
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decrypt token."""
        try:
            # Decode and decrypt
            encrypted_token = base64.urlsafe_b64decode(token.encode())
            decrypted_data = self.fernet.decrypt(encrypted_token)
            token_data = json.loads(decrypted_data.decode())
            
            # Check expiration
            expires = datetime.fromisoformat(token_data['expires'])
            if datetime.utcnow() > expires:
                logger.warning("Token has expired")
                return None
            
            return token_data['data']
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def refresh_token(self, token: str, extends_hours: int = EncryptionConfig.TOKEN_EXPIRY_HOURS) -> Optional[str]:
        """Refresh token with new expiration."""
        data = self.verify_token(token)
        if data:
            return self.create_token(data, extends_hours)
        return None


class SecureSessionManager:
    """Secure session management with encryption."""
    
    def __init__(self, encryption: DataEncryption, token_manager: TokenManager):
        """Initialize session manager."""
        self.encryption = encryption
        self.token_manager = token_manager
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Create encrypted session."""
        session_id = secrets.token_urlsafe(32)
        
        # Encrypt sensitive session data
        encrypted_data = {}
        for key, value in session_data.items():
            if isinstance(value, str) and self._is_sensitive_field(key):
                encrypted_data[key] = self.encryption.encrypt_data(value)
            else:
                encrypted_data[key] = value
        
        # Store session
        self.sessions[session_id] = {
            'user_id': user_id,
            'data': encrypted_data,
            'created': datetime.utcnow().isoformat(),
            'last_accessed': datetime.utcnow().isoformat()
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get and decrypt session data."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Update last accessed
        session['last_accessed'] = datetime.utcnow().isoformat()
        
        # Decrypt sensitive data
        decrypted_data = {}
        for key, value in session['data'].items():
            if isinstance(value, dict) and 'ciphertext' in value:
                decrypted_data[key] = self.encryption.decrypt_data(value)
            else:
                decrypted_data[key] = value
        
        return {
            'user_id': session['user_id'],
            'data': decrypted_data,
            'created': session['created'],
            'last_accessed': session['last_accessed']
        }
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data."""
        if session_id not in self.sessions:
            return False
        
        # Encrypt sensitive updates
        encrypted_updates = {}
        for key, value in updates.items():
            if isinstance(value, str) and self._is_sensitive_field(key):
                encrypted_updates[key] = self.encryption.encrypt_data(value)
            else:
                encrypted_updates[key] = value
        
        # Update session
        self.sessions[session_id]['data'].update(encrypted_updates)
        self.sessions[session_id]['last_accessed'] = datetime.utcnow().isoformat()
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """Clean up expired sessions."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            last_accessed = datetime.fromisoformat(session['last_accessed'])
            if last_accessed < cutoff:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if field contains sensitive data that should be encrypted."""
        sensitive_fields = {
            'password', 'token', 'api_key', 'secret', 'private_key',
            'ssn', 'credit_card', 'bank_account', 'personal_data'
        }
        return any(sensitive in field_name.lower() for sensitive in sensitive_fields)


class DataAnonymizer:
    """Data anonymization utilities for testing and compliance."""
    
    @staticmethod
    def anonymize_email(email: str) -> str:
        """Anonymize email address."""
        if '@' not in email:
            return "anonymous@example.com"
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            anonymized_local = 'xx'
        else:
            anonymized_local = local[0] + 'x' * (len(local) - 2) + local[-1]
        
        return f"{anonymized_local}@{domain}"
    
    @staticmethod
    def anonymize_name(name: str) -> str:
        """Anonymize personal name."""
        parts = name.split()
        if not parts:
            return "Anonymous User"
        
        anonymized_parts = []
        for part in parts:
            if len(part) <= 1:
                anonymized_parts.append('X')
            else:
                anonymized_parts.append(part[0] + 'x' * (len(part) - 1))
        
        return ' '.join(anonymized_parts)
    
    @staticmethod
    def anonymize_phone(phone: str) -> str:
        """Anonymize phone number."""
        # Keep only digits
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 4:
            return "XXX-XXX-XXXX"
        
        # Keep last 4 digits
        return f"XXX-XXX-{digits[-4:]}"
    
    @staticmethod
    def anonymize_document_content(content: str) -> str:
        """Anonymize document content by replacing sensitive patterns."""
        import re
        
        # Email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                        'email@example.com', content)
        
        # Phone numbers
        content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'XXX-XXX-XXXX', content)
        
        # SSN patterns
        content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', 'XXX-XX-XXXX', content)
        
        # Credit card patterns
        content = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 
                        'XXXX-XXXX-XXXX-XXXX', content)
        
        return content
    
    @staticmethod
    def create_test_dataset(original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create anonymized test dataset."""
        anonymized = {}
        
        for key, value in original_data.items():
            if isinstance(value, str):
                if 'email' in key.lower():
                    anonymized[key] = DataAnonymizer.anonymize_email(value)
                elif 'name' in key.lower():
                    anonymized[key] = DataAnonymizer.anonymize_name(value)
                elif 'phone' in key.lower():
                    anonymized[key] = DataAnonymizer.anonymize_phone(value)
                elif 'content' in key.lower():
                    anonymized[key] = DataAnonymizer.anonymize_document_content(value)
                else:
                    anonymized[key] = value
            elif isinstance(value, dict):
                anonymized[key] = DataAnonymizer.create_test_dataset(value)
            elif isinstance(value, list):
                anonymized[key] = [
                    DataAnonymizer.create_test_dataset(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                anonymized[key] = value
        
        return anonymized


# Global instances
data_encryption = DataEncryption()
token_manager = TokenManager(os.getenv('JWT_SECRET_KEY', 'default-secret-key'))
session_manager = SecureSessionManager(data_encryption, token_manager)