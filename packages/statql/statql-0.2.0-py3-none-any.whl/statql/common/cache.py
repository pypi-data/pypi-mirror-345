import json
import os
import typing
from datetime import timedelta, datetime
from threading import Lock

from pydantic import Field

from .utils import FrozenModel, Model


class _CacheValue(FrozenModel):
    value: typing.Any
    expiration: datetime


class _Cache(Model):
    key_to_value: typing.MutableMapping[str, _CacheValue] = Field(default_factory=dict)


class CacheManager:
    def __init__(self, *, file_path: str):
        self._file_path = file_path

        try:
            with open(self._file_path, "r") as f:
                self._cache = _Cache(**json.load(f))
        except FileNotFoundError:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self._cache = _Cache()

        self._lock = Lock()  # TODO: improve

    def store(self, *, key: str, value: typing.Any, ttl: timedelta) -> None:
        with self._lock:  # TODO: periodic write
            self._cache.key_to_value[key] = _CacheValue(value=value, expiration=datetime.now() + ttl)

            with open(self._file_path, "w") as f:
                json.dump(self._cache.model_dump(mode="json"), f)

    def fetch(self, *, key: str) -> typing.Any | LookupError:
        if value := self._cache.key_to_value.get(key):
            if datetime.now() < value.expiration:
                return value.value

        raise LookupError
