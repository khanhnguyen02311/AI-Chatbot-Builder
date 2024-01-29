import uuid
from datetime import timedelta, datetime
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select, or_
from pydantic import BaseModel, ConfigDict, Field
from configurations import Security
from components.data import POSTGRES_SESSION_FACTORY, REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import postgres as PostgresSchemas
from components.repositories.account import AccountRepository

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

DEFAULT_PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__default_rounds=11)
DEFAULT_OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/auth/signin", scheme_name="JWT")


class Token(BaseModel):
    id: int
    type: str


def _create_token(user_identifier: int, token_type: str) -> str:
    """Return the token based on the subject (account)"""

    now = datetime.utcnow()
    to_encode = {"iat": now, "sub": Token(id=user_identifier, type=token_type).model_dump()}
    if token_type == "access":
        to_encode["exp"] = now + timedelta(minutes=Security.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token_type == "refresh":
        to_encode["exp"] = now + timedelta(minutes=Security.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode["jti"] = str(uuid.uuid4())
    else:
        to_encode["exp"] = now + timedelta(minutes=30)
    encoded_jwt = jwt.encode(to_encode, Security.JWT_SECRET_KEY, Security.JWT_ALGORITHM)
    return encoded_jwt


def _decode_token(token: str) -> dict:
    """Decode the token and return the internal payload"""

    payload = jwt.decode(token, Security.JWT_SECRET_KEY, algorithms=[Security.JWT_ALGORITHM],
                         options={"verify_exp": True, "require_sub": False, "verify_sub": False})
    return payload


def _create_hash(password) -> str:
    return DEFAULT_PASSWORD_CONTEXT.hash(password)


def _validate_hash(plain_password, hashed_password) -> bool:
    valid, updated_hash = DEFAULT_PASSWORD_CONTEXT.verify_and_update(plain_password, hashed_password)
    if updated_hash is not None:
        pass  # update to new hash, implement later
    return valid


class AccountService:
    def __init__(self, session):
        self.session = session
        self.repository = AccountRepository(session=session)

    @classmethod
    def validate_token(cls, token: str = Depends(DEFAULT_OAUTH2_SCHEME)):
        try:
            payload = _decode_token(token)
            if payload["type"] != ACCESS_TOKEN_TYPE:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            with POSTGRES_SESSION_FACTORY.begin() as session:
                repository = AccountRepository(session=session)
                account = repository.get(identifier=payload["id"])
                if account is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
                return account
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @classmethod
    def deactivate_token(cls, token: str = Depends(DEFAULT_OAUTH2_SCHEME)):
        try:
            payload = _decode_token(token)
            if payload["type"] != REFRESH_TOKEN_TYPE:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            REDIS_SESSION.setex(f"Logout:{payload['jti']}", Security.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60, "1")
        except (jwt.ExpiredSignatureError, jwt.JWTError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @classmethod
    def renew_token(cls, token: str = Depends(DEFAULT_OAUTH2_SCHEME)):
        try:
            payload = _decode_token(token)
            if payload["type"] != REFRESH_TOKEN_TYPE:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            if REDIS_SESSION.get(f"Logout:{payload['jti']}") is not None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            with POSTGRES_SESSION_FACTORY.begin() as session:
                repository = AccountRepository(session=session)
                account = repository.get(identifier=payload["id"])
                if account is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
                account_tokens = {
                    "access_token": _create_token(account.id, ACCESS_TOKEN_TYPE),
                    "refresh_token": _create_token(account.id, REFRESH_TOKEN_TYPE),
                    "token_type": "bearer",
                }
                return account_tokens
        except (jwt.ExpiredSignatureError, jwt.JWTError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def create_account(self, data: PostgresSchemas.AccountPOST):
        account_query = select(PostgresModels.Account).where(or_(PostgresModels.Account.username == data.username, PostgresModels.Account.email == data.email))
        if self.session.scalars(account_query).first() is not None:
            return None, "Username or email existed"
        new_account = PostgresModels.Account(**data.model_dump(exclude={"password"}),
                                             password=_create_hash(data.password))
        self.repository.create(new_account=new_account)
        return new_account, None

    def validate_account(self, data: PostgresSchemas.AccountLOGIN) -> tuple[Any, Any]:
        account_query = select(PostgresModels.Account).where(or_(PostgresModels.Account.username == data.username_or_email, PostgresModels.Account.email == data.username_or_email))
        account = self.session.scalars(account_query).first()
        if account is None or not _validate_hash(data.password, account.password):
            return None, "Wrong username or password"
        account_tokens = {
            "access_token": _create_token(account.id, ACCESS_TOKEN_TYPE),
            "refresh_token": _create_token(account.id, REFRESH_TOKEN_TYPE),
            "token_type": "bearer",
        }
        return account_tokens, None

    def edit_account_information(self, identifier: int, data: PostgresSchemas.AccountPUT):
        new_account_info = self.repository.update(identifier=identifier, new_data=data)
        if new_account_info is None:
            return None, "Account not found"
        return new_account_info, None
