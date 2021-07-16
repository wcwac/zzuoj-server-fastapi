import datetime
import hashlib
import json
from typing import Optional, Dict

from fastapi import Header
from jose import jwt

import settings


def gettime() -> str:
    now_time = str(datetime.datetime.now()).split('.')[0]
    now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
    return str(now_time)


def MD5(string: str) -> str:
    h = hashlib.md5()
    h.update(string.encode(encoding='utf-8'))
    return h.hexdigest()


def saltMD5(string: str) -> str:
    return MD5(MD5(string) + settings.SALT)


def create_jwt(payload) -> str:
    """
    :param payload: Dict
    :return: encoded_jwt
    """
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"exp": expire, "sub": json.dumps(payload)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY)
    return encoded_jwt


def checkjwt(jwtstr):
    try:
        jwtdata = jwt.decode(jwtstr, settings.JWT_SECRET_KEY)
        return jwtdata
    except:
        return None


def check_jwt_token(
        token: Optional[str] = Header(..., alias="Authorization")
) -> Dict:
    """Authorization
    解析验证 headers中为token的值 当然也可以用 Header(..., alias="Authentication") 或者 alias="X-token"
    :param token
    :return: payload
    :raise: JWTError
    """

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY)
        return payload
    except (jwt.JWTError, jwt.ExpiredSignatureError, AttributeError):
        # 抛出自定义异常， 然后捕获统一响应
        raise jwt.JWTError


if __name__ == "__main__":
    string = "MD5加密"
    print('MD5加密前为:' + string)
    print('MD5加密后为:' + MD5(string))
