try:
    import boto3
except ImportError:
    boto3 = None
else:
    boto3 = boto3.client("kms", region_name=region)


class AWSKMSProvider(KeyProvider):
    def __init__(self, kms_key_id: str, region: str = None):
        self.kms = boto3.client("kms", region_name=region)
        self.key_id = kms_key_id

    def generate_data_key(self, key_id=None):
        resp = self.kms.generate_data_key(
            KeyId=key_id or self.key_id, KeySpec="AES_256"
        )
        return resp["Plaintext"], resp["CiphertextBlob"]

    def encrypt(self, plaintext: bytes, key_id=None):
        # direct KMS encrypt (slower, size-limited) or envelope as fallback
        resp = self.kms.encrypt(KeyId=key_id or self.key_id, Plaintext=plaintext)
        return resp["CiphertextBlob"]

    def decrypt(self, ciphertext: bytes):
        resp = self.kms.decrypt(CiphertextBlob=ciphertext)
        return resp["Plaintext"]


class KMSEncryptedModel(SecureModel):
    provider: ClassVar[KeyProvider] = AWSKMSProvider(settings.KMS_KEY_ID)

    def encrypt_data(self):
        for field, pt in self.pending_encryption_fields.items():
            # envelope encrypt
            dek, edek = self.provider.generate_data_key()
            ct = Fernet(base64.urlsafe_b64encode(dek)).encrypt(pt.encode())
            # store “edek|ct”
            setattr(self, field, base64.b64encode(edek + b"|" + ct).decode())

    def decrypt_data(self):
        for field, blob in self.pending_decryption_fields.items():
            raw = base64.b64decode(blob.encode())
            edek, ct = raw.split(b"|", 1)
            dek = self.provider.decrypt(edek)
            pt = Fernet(base64.urlsafe_b64encode(dek)).decrypt(ct).decode()
            setattr(self, field, pt)
