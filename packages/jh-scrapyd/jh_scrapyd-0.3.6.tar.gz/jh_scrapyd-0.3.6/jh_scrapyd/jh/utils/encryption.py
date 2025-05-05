import hashlib
import base64
import json
from urllib.parse import quote
from collections.abc import Iterable
from jh_scrapyd import get_config


class Md5Encryption:
    @staticmethod
    def _calculate_md5(content: str) -> hashlib.md5:
        md5 = hashlib.md5()
        md5.update(content.encode("utf-8"))
        return md5

    @classmethod
    def md5_upper32(cls, content: str) -> str:
        return cls._calculate_md5(content).hexdigest().upper()

    @classmethod
    def md5_upper16(cls, content: str) -> str:
        return cls._calculate_md5(content).hexdigest()[8:-8].upper()

    @classmethod
    def md5_lower32(cls, content: str) -> str:
        return cls._calculate_md5(content).hexdigest().lower()

    @classmethod
    def md5_lower16(cls, content: str) -> str:
        return cls._calculate_md5(content).hexdigest()[8:-8].lower()


class Base64Encryption:
    @staticmethod
    def _to_format(data) -> bytes:
        if isinstance(data, str):
            return data.encode("utf-8")
        if isinstance(data, bytes):
            return data
        raise TypeError("Input must be of type str or bytes")

    @classmethod
    def encode(cls, data) -> str:
        return base64.b64encode(cls._to_format(data)).decode("ascii")

    @classmethod
    def decode(cls, data) -> str:
        return base64.b64decode(cls._to_format(data)).decode("ascii")


class ApiSign:
    API_KEY = get_config(option="signature_key", section="api")

    @classmethod
    def verify_sign(cls, params: dict) -> bool:
        sign = params.pop("sign", None)
        return sign == cls.create_sign(params)

    @classmethod
    def create_sign(cls, params: dict) -> str:
        sorted_items = sorted(params.items())
        components = []

        for name, value in sorted_items:
            if isinstance(value, Iterable) and not isinstance(value, str):
                value = Base64Encryption.encode(json.dumps(value, separators=(",", ":"), ensure_ascii=False))
            elif value is None:
                value = ""
            else:
                value = str(value)

            # 将编码后的值添加到components列表中
            components.append(f"{name}={value}")

        # 将components连接成签名字符串，并添加API_KEY
        sign_string = "&".join(components) + f"&api_key={cls.API_KEY}"
        return Md5Encryption.md5_lower32(sign_string)

    @classmethod
    def set_api_key(cls, api_key: str):
        cls.API_KEY = api_key
