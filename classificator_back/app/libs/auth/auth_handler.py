from datetime import datetime, timedelta

from passlib.context import CryptContext
import jwt

from app.schemas.schema import Response
from app.settings import Settings

settings = Settings()


class Auth:
    hasher = CryptContext(schemes=['sha256_crypt'])

    @classmethod
    async def encode_password(cls, password):
        return cls.hasher.hash(password)

    @classmethod
    async def verify_password(cls, password, encoded_password):
        return cls.hasher.verify(password, encoded_password)

    @classmethod
    async def get_access_token(cls, user):
        token = jwt.encode(payload={'user': user,
                                        'exp': datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expires_in),
                                        'iat': datetime.utcnow(), },
                               key=settings.jwt_access_token_secret,
                               algorithm="HS256",
                               )
        return token

    @classmethod
    async def get_refresh_token(cls, user):

        token = jwt.encode(payload={'user': user,
                                    'exp': datetime.utcnow() + timedelta(minutes=settings.jwt_refresh_token_expires_in),
                                    'iat': datetime.utcnow(), },
                           key=settings.jwt_refresh_token_secret,
                           algorithm="HS256",
                           )
        return token

    @classmethod
    async def decode_access_token(cls, token):
        try:
            data = jwt.decode(token, key=settings.jwt_access_token_secret, algorithms="HS256")
            return Response(data=data,
                            error=None,
                            success=True)
        except jwt.ExpiredSignatureError:
            return Response(error={'code': 10009,
                                      'msg': 'Срок действия акссес токена истек'},
                            data=None,
                                success=False)
        except jwt.DecodeError:
            return Response(error={'code': 10010,
                                   'msg': 'Ошибка расшифровки аксесс токена'},
                            data=None,
                            success=False)

    @classmethod
    async def decode_refresh_token(cls, token):
        try:
            data = jwt.decode(token, key=settings.jwt_refresh_token_secret, algorithms="HS256")
            return Response(data=data,
                            error=None,
                            success=True)
        except jwt.ExpiredSignatureError:
            return Response(error={'code': 10009,
                                   'msg': 'Срок действия рефреш токена истек'},
                            data=None,
                            success=False)
        except jwt.DecodeError:
            return Response(error={'code': 10010,
                                   'msg': 'Ошибка расшифровки рефреш токена'},
                            data=None,
                            success=False)