from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

class Identity:
    """Генерация ключей и операции с ними"""

    def __init__(self, private_key: X25519PrivateKey):
        """Инициализация ключей"""
        self._private_key = private_key
        self._public_key = private_key.public_key()

    @property
    def private_key(self) -> X25519PrivateKey:
        """Возвращает приватный ключ"""
        return self._private_key
    
    @property
    def public_key(self) -> X25519PublicKey:
        """Возвращает публичный ключ"""
        return self._public_key
    
    @classmethod
    def generate(cls):
        """Генерация новой пары ключей"""
        private_key = X25519PrivateKey.generate()
        return cls(private_key)
    
    @classmethod
    def from_bytes(cls, private_bytes: bytes):
        """Загрузка приватного и публичного ключей из байтов"""
        return cls(X25519PrivateKey.from_private_bytes(private_bytes))
    
    def shared_secret(self, peer_public_key: bytes | X25519PublicKey) -> bytes:
        """Возвращает общий секрет"""
        if isinstance(peer_public_key, bytes):
            peer_public_key = X25519PublicKey.from_public_bytes(peer_public_key)
        return self._private_key.exchange(peer_public_key)
