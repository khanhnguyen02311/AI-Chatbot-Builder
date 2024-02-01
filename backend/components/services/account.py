import uuid
from datetime import timedelta, datetime
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select, and_, or_
from pydantic import BaseModel, ConfigDict, Field
from configurations import Security
from components.data import POSTGRES_SESSION_FACTORY, REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import account as AccountSchemas
from components.repositories.account import AccountRepository
from components.repositories.account_role import AccountRoleRepository

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

# problems with bcrypt library in passlib
# DEFAULT_PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__default_rounds=11)
DEFAULT_PASSWORD_CONTEXT = CryptContext(schemes=["sha256_crypt"], deprecated="auto", sha256_crypt__default_rounds=400000)
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
    assert "sub" in payload and "id" in payload["sub"] and "type" in payload["sub"], "Invalid token"
    return payload


def _create_hash(password) -> str:
    return DEFAULT_PASSWORD_CONTEXT.hash(password)


def _validate_hash(plain_password, hashed_password) -> bool:
    valid, updated_hash = DEFAULT_PASSWORD_CONTEXT.verify_and_update(plain_password, hashed_password)
    if updated_hash is not None:
        pass  # update to new hash, implement later
    return valid


class AccountService:
    """Handle all business logic related to account, including authentication and authorization"""

    def __init__(self, session):
        self.session = session
        self.repository = AccountRepository(session=session)

    @classmethod
    def validate_token(cls, token: str = Depends(DEFAULT_OAUTH2_SCHEME)):
        try:
            payload = _decode_token(token)
            if payload["sub"]["type"] != ACCESS_TOKEN_TYPE:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            with POSTGRES_SESSION_FACTORY.begin() as session:
                repository = AccountRepository(session=session)
                account = repository.get(identifier=payload["sub"]["id"])
                if account is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
                session.expunge_all()
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
            print(payload)
            if payload["sub"]["type"] != REFRESH_TOKEN_TYPE:
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
            if payload["sub"]["type"] != REFRESH_TOKEN_TYPE:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            if REDIS_SESSION.get(f"Logout:{payload['jti']}") is not None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            with POSTGRES_SESSION_FACTORY.begin() as session:
                repository = AccountRepository(session=session)
                account = repository.get(identifier=payload["sub"]["id"])
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

    def create_account(self, data: AccountSchemas.AccountPOST):
        account_role_user = AccountRoleRepository(session=self.session).get_by_role(role="User")
        if account_role_user is None:
            return None, "Account role not found"
        account_query = select(PostgresModels.Account).where(
            and_(
                or_(PostgresModels.Account.username == data.username, PostgresModels.Account.email == data.email),
                PostgresModels.Account.id_account_role == account_role_user.id))
        if self.session.scalars(account_query).first() is not None:
            return None, "Username or email existed"
        new_account = PostgresModels.Account(**data.model_dump(exclude={"password"}),
                                             password=_create_hash(data.password),
                                             id_account_role=account_role_user.id)
        self.repository.create(new_account=new_account)
        return new_account, None

    def validate_account(self, data: AccountSchemas.AccountLOGIN) -> tuple[Any, Any]:
        account_role_user = AccountRoleRepository(session=self.session).get_by_role(role="User")
        account_query = select(PostgresModels.Account).where(
            and_(
                or_(PostgresModels.Account.username == data.username_or_email, PostgresModels.Account.email == data.username_or_email),
                PostgresModels.Account.id_account_role == account_role_user.id))
        account = self.session.scalars(account_query).first()
        if account is None or not _validate_hash(data.password, account.password):
            return None, "Wrong username or password"
        account_tokens = {
            "access_token": _create_token(account.id, ACCESS_TOKEN_TYPE),
            "refresh_token": _create_token(account.id, REFRESH_TOKEN_TYPE),
            "token_type": "bearer",
        }
        return account_tokens, None

    def get_account_information(self, identifier: int):
        account_info = self.repository.get(identifier=identifier)
        if account_info is None:
            return None, "Account not found"
        return account_info, None

    def edit_account_information(self, identifier: int, data: AccountSchemas.AccountPUT):
        new_account_info = self.repository.update(identifier=identifier, new_data=data)
        if new_account_info is None:
            return None, "Account not found"
        return new_account_info, None
