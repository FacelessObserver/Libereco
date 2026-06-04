from os import urandom
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .config import IMK, SALT_SIZE, NONCE_SIZE, TAG_SIZE

class Crypt:
    """
    Криптографические операции над данными, представленными в байтах
    Формат пакета: [SALT] + [NONCE] + [TAG + cipher_data]
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def derive_message_key(cls, shared_secret: bytes, salt: bytes | None = None) -> tuple[bytes, bytes]:
        """Выводит уникальный ключ из общего секрета"""
        if salt is None:
            salt = urandom(SALT_SIZE)
        message_key = HKDF(algorithm = SHA256(), length = 32, salt = salt, info = IMK).derive(shared_secret)
        return message_key, salt
    
    @classmethod
    def encrypt(cls, data: bytes, shared_secret: bytes) -> bytes:
        """Шифрует данные, представленные в байтах. Возвращает пакет: salt + nonce + cipher_data"""
        message_key, salt = cls.derive_message_key(shared_secret)
        nonce = urandom(NONCE_SIZE)
        cipher_data = AESGCM(message_key).encrypt(nonce, data, None)
        return salt + nonce + cipher_data
    
    @classmethod
    def decrypt(cls, packet: bytes, shared_secret: bytes) -> bytes:
        """Дешифрует пакет данных, представленный в байтах"""
        if len(packet) < SALT_SIZE + NONCE_SIZE + TAG_SIZE:
            raise ValueError("Пакет слишком маленький")
        salt = packet[: SALT_SIZE]
        nonce = packet[SALT_SIZE : SALT_SIZE + NONCE_SIZE]
        cipher_data = packet[SALT_SIZE + NONCE_SIZE:]
        message_key, _ = cls.derive_message_key(shared_secret, salt)
        try:
            return AESGCM(message_key).decrypt(nonce, cipher_data, None)
        except:
            raise ValueError("Ошибка при дешифровке")
