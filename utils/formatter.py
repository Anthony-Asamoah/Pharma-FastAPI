from datetime import datetime, timezone
from json import dumps, loads
from re import sub
from typing import Any


class Formatter:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Formatter, cls).__new__(cls)
        return cls.__instance

    @staticmethod
    def bytes_to_str(obj: bytes | bytearray):
        str_payload = obj.decode("utf-8")
        return loads(str_payload)

    @staticmethod
    def datetime_to_isoformat(date_time: datetime) -> str:
        return date_time.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def str_to_bytes(obj: dict[Any, Any]):
        json_str = dumps(obj)
        return json_str.encode("utf-8")

    @staticmethod
    def camel_to_snake(key: str) -> str:
        snake_case_key = sub("(.)([A-Z][a-z]+)", r"\1_\2", key)
        return sub("([a-z0-9])([A-Z])", r"\1_\2", snake_case_key).lower()

    @staticmethod
    def snake_to_camel(key: str) -> str:
        words = key.split("_")
        return words[0] + "".join(letter.title() for letter in words[1:])

    @staticmethod
    def dict_key_to_camel_case(dict_key: str) -> str:
        return "".join(word if idx == 0 else word.capitalize() for idx, word in enumerate(dict_key.split("_")))


fmt = Formatter()
