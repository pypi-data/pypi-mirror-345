from abc import ABC, abstractmethod


class KeyProvider(ABC):
    @abstractmethod
    def encrypt(self, plaintext: bytes, key_id: str, **ctx) -> bytes:
        """Use the remote KMS to encrypt data-key or data directly."""

    @abstractmethod
    def decrypt(self, ciphertext: bytes, **ctx) -> bytes:
        """Use the remote KMS to decrypt data-key or data directly."""

    @abstractmethod
    def generate_data_key(self, key_id: str) -> tuple[bytes, bytes]:
        """
        For envelope encryption: returns (plaintext_data_key, encrypted_data_key)
        """
