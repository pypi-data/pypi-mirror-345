import string
import random
import base64
import hashlib
import hmac
from enum import Enum
from typing import TypeVar

T = TypeVar("T")


def action(path, method="POST"):

    def decorator(function: T) -> T:
        def wrapper(*args, **kwargs):
            kwargs.update({"path": path, "method": method})
            return function(*args, **kwargs)

        wrapper.__doc__ = function.__doc__
        return wrapper

    return decorator


def get_random_key():
    all_characters = string.ascii_letters + string.digits
    # 生成5位随机字符串
    random_key = ''.join(random.choice(all_characters) for _ in range(5))
    return random_key

def get_signature(open_key_id, secret_key, path, timestamp, random_key):
    value = f"{open_key_id}&{timestamp}&{path}"
    key = f"{secret_key}{random_key}"
    hmac_result = hmac.new(key.encode('utf-8'), value.encode('utf-8'), hashlib.sha256).digest()
    hex_signature = hmac_result.hex()
    base64_signature = base64.b64encode(hex_signature.encode('utf-8')).decode('utf-8')
    final_signature = f"{random_key}{base64_signature}"
    print(f"步骤五 - 最终签名: {final_signature}")
    return final_signature


class ShopType(Enum):
    SELF_OPERATION = 'SELF_OPERATION' # '自运营'
    SEMI_MANAGED = 'SEMI_MANAGED' #'半托管'
    FULL_MANAGED = 'FULL_MANAGED' #'全托管'
    SELF_OWNED = 'SELF_OWNED' #'自营'
    OTHER = 'OTHER' # '其他'