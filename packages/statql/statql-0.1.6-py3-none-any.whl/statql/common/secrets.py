import json
import os
import random
import string
import typing
from threading import Lock

import keyring
from cryptography.fernet import Fernet

from .definitions import STATQL_APP_DATA_PATH


class SecretsManager:
    _SECRETS_FILE_PATH = os.path.join(STATQL_APP_DATA_PATH, "secrets")
    _KEYRING_IDENTIFIERS = ("statql", "secrets_file_keyring")

    _secrets: typing.Dict[str, str] | None = None
    _lock = Lock()

    @classmethod
    def get_secret(cls, *, secret_name: str) -> str:
        with cls._lock:
            if cls._secrets is None:
                cls._secrets = cls._load_secrets()

            if secret_name not in cls._secrets:
                raise LookupError(f"Secret not found: {secret_name}")

            return cls._secrets[secret_name]

    @classmethod
    def store_secret(cls, *, secret_name_prefix: str, secret_value: str) -> str:
        with cls._lock:
            if cls._secrets is None:
                cls._secrets = cls._load_secrets()

            suffix = "".join(random.choices(string.ascii_letters + string.digits, k=10))
            secret_name = f"{secret_name_prefix}-{suffix}"

            cls._secrets[secret_name] = secret_value
            cls._save_secrets(secrets=cls._secrets)

            return secret_name

    @classmethod
    def delete_secret(cls, *, secret_name: str) -> None:
        with cls._lock:
            if cls._secrets is None:
                cls._secrets = cls._load_secrets()

            if secret_name not in cls._secrets:
                raise LookupError(f"Secret not found: {secret_name}")

            cls._secrets.pop(secret_name)
            cls._save_secrets(secrets=cls._secrets)

    @classmethod
    def _load_secrets(cls) -> typing.Dict[str, str]:
        secrets_file_key = cls._get_secrets_file_key()

        try:
            with open(cls._SECRETS_FILE_PATH, "rb") as f:
                encrypted_data = f.read()
                plaintext = Fernet(secrets_file_key).decrypt(encrypted_data).decode(encoding="utf-8")
                return json.loads(plaintext)

        except FileNotFoundError:
            return {}

    @classmethod
    def _save_secrets(cls, *, secrets: typing.Dict[str, str]) -> None:
        secrets_file_key = cls._get_secrets_file_key()

        with open(cls._SECRETS_FILE_PATH, "wb") as f:
            plaintext = json.dumps(secrets)
            encrypted_data = Fernet(secrets_file_key).encrypt(plaintext.encode(encoding="utf-8"))
            f.write(encrypted_data)

    @classmethod
    def _get_secrets_file_key(cls) -> bytes:
        keyring_service, keyring_username = cls._KEYRING_IDENTIFIERS

        secrets_file_key = keyring.get_password(keyring_service, keyring_username)

        if secrets_file_key is None:
            secrets_file_key = Fernet.generate_key().decode()
            keyring.set_password(keyring_service, keyring_username, secrets_file_key)

        return secrets_file_key.encode(encoding="utf-8")
