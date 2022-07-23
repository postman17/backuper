from cryptography.fernet import Fernet

from django.conf import settings
from django.utils.encoding import smart_bytes, smart_str


class EncryptDecryptWrapper:
    DEFAULT_FIELDS = [
        'client_id',
        'client_secret',
        'access_token',
        'refresh_token',
        'master_password',
    ]

    @classmethod
    def encrypt(cls, data, key=None):
        """Encrypt string by key."""
        key = key or settings.MASTER_PASSWORD
        fernet = Fernet(key)
        data = fernet.encrypt(smart_bytes(data))
        return data

    @classmethod
    def decrypt(cls, data, key=None):
        """Decrypt string by key."""
        key = key or settings.MASTER_PASSWORD
        fernet = Fernet(key)
        data = fernet.decrypt(smart_bytes(data))
        return data

    @classmethod
    def encrypt_sensitive_fields(cls, data: dict, fields: list = None) -> dict:
        """Encrypt sensitive dict values by keys."""
        default_fields = [
            'client_id',
            'client_secret',
            'access_token',
            'refresh_token',
            'master_password',
        ]
        if fields:
            default_fields = fields

        result_data = {}
        for key, value in data.items():
            if key in default_fields:
                result_data[key] = smart_str(cls.encrypt(value))
            else:
                result_data[key] = value

        return result_data

    @classmethod
    def decrypt_sensitive_fields(cls, data: dict, fields: list = None) -> dict:
        """Decrypt sensitive dict values by keys."""
        default_fields = cls.DEFAULT_FIELDS
        if fields:
            default_fields = fields

        result_data = {}
        for key, value in data.items():
            if key in default_fields:
                result_data[key] = smart_str(cls.decrypt(value))
            else:
                result_data[key] = value

        return result_data

    @classmethod
    def mask_sensitive_data(cls, data: dict, fields: list = None) -> dict:
        default_fields = cls.DEFAULT_FIELDS
        if fields:
            default_fields = fields

        result_data = {}
        for key, value in data.items():
            if key in default_fields:
                result_data[key] = f"***{key}-masked***"
            else:
                result_data[key] = value

        return result_data

    @classmethod
    def get_decrypted_value(cls, data: dict, data_key: str, crypto_key=None) -> str:
        """Get decrypted value by dict key."""
        result_data = None
        encrypted_value = data.get(data_key)
        if encrypted_value:
            result_data = cls.decrypt(encrypted_value, key=crypto_key)

        return smart_str(result_data)
