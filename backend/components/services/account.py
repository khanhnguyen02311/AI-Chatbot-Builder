import uuid
from datetime import timezone, datetime, timedelta
from typing import Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select, and_, or_
from pydantic import BaseModel
from configurations.envs import Security
from components.data import POSTGRES_SESSION_FACTORY, REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import account as AccountSchemas, chat_account as ChatAccountSchemas
from components.repositories.account import AccountRepository
from components.repositories.account_role import AccountRoleRepository
from components.repositories.chat_account import ChatAccountRepository

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

DEFAULT_OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/auth/signin", scheme_name="JWT")


class Token(BaseModel):
    id: int
    chat_id: int | None = None
    type: str


def _create_token(account_identifier: int, token_type: str, chat_account_identifier: int | None = None) -> str:
    """Return the token based on the subject (account)"""

    now = datetime.now(timezone.utc)
    to_encode = {
        "iat": now,
        "sub": Token(id=account_identifier, chat_id=chat_account_identifier, type=token_type).model_dump(),
    }
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

    payload = jwt.decode(
        token,
        Security.JWT_SECRET_KEY,
        algorithms=[Security.JWT_ALGORITHM],
        options={"verify_exp": True, "require_sub": False, "verify_sub": False},
    )
    assert "sub" in payload and "id" in payload["sub"] and "type" in payload["sub"], "Invalid token"
    return payload


def _create_hash(password) -> str:
    return Security.DEFAULT_PASSWORD_CONTEXT.hash(password)


def _validate_hash(plain_password, hashed_password) -> bool:
    valid, updated_hash = Security.DEFAULT_PASSWORD_CONTEXT.verify_and_update(plain_password, hashed_password)
    if updated_hash is not None:
        pass  # update to new hash, implement later
    return valid


class AccountService:
    """Handle complex logic related to account, including authentication and authorization"""

    def __init__(self, session):
        self.session = session
        self.repository = AccountRepository(session=session)

    @classmethod
    def validate_token(cls, token: str = Depends(DEFAULT_OAUTH2_SCHEME), return_type: str = "account"):
        try:
            payload = _decode_token(token)
            if payload["sub"]["type"] != ACCESS_TOKEN_TYPE:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            with POSTGRES_SESSION_FACTORY.begin() as session:
                if return_type == "account":
                    account_data = AccountRepository(session=session).get(identifier=payload["sub"]["id"])
                elif return_type == "chat_account":
                    account_data = ChatAccountRepository(session=session).get(identifier=payload["sub"]["chat_id"])
                if account_data is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
                session.expunge_all()
            return account_data
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @classmethod
    def validate_token_chat(cls, token: str = Depends(DEFAULT_OAUTH2_SCHEME)):
        return cls.validate_token(token=token, return_type="chat_account")

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
                account = AccountRepository(session=session).get(identifier=payload["sub"]["id"])
                if account is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
                chat_account = ChatAccountRepository(session=session).get_by_account_type(
                    account.id, PostgresModels.CONSTANTS.ChatAccount_account_type[0]
                )
                if chat_account is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
                account_tokens = {
                    "access_token": _create_token(account.id, ACCESS_TOKEN_TYPE, chat_account_identifier=chat_account.id),
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

    def create_account_pair(self, data: AccountSchemas.AccountPOST) -> tuple[Any, Any]:
        user_role = AccountRoleRepository(session=self.session).get_by_role(
            role=PostgresModels.CONSTANTS.AccountRole_role[1]
        )
        if user_role is None:
            return [], "Account role not found"
        account_query = select(PostgresModels.Account).where(
            and_(
                or_(PostgresModels.Account.username == data.username, PostgresModels.Account.email == data.email),
                PostgresModels.Account.id_account_role == user_role.id,
            )
        )
        if self.session.scalars(account_query).first() is not None:
            return [], "Username or email existed"
        # create account
        new_account = PostgresModels.Account(
            **data.model_dump(exclude={"password"}), password=_create_hash(data.password), id_account_role=user_role.id
        )
        self.repository.create(new_account=new_account)
        # create chat account
        new_chat_account = PostgresModels.ChatAccount(
            account_type=PostgresModels.CONSTANTS.ChatAccount_account_type[0], id_internal_account=new_account.id
        )
        ChatAccountRepository(session=self.session).create(new_chat_account)
        return [new_account, new_chat_account], None

    def create_chat_account(self, data: ChatAccountSchemas.ChatAccountPOST) -> tuple[Any, Any]:
        new_chat_account = PostgresModels.ChatAccount(**data.model_dump(exclude_none=True))
        ChatAccountRepository(session=self.session).create(new_chat_account)
        return new_chat_account, None

    def validate_account(self, data: AccountSchemas.AccountLOGIN, admin_required=False) -> tuple[Any, Any]:
        role_id = 0 if admin_required else 1
        user_role = AccountRoleRepository(session=self.session).get_by_role(
            role=PostgresModels.CONSTANTS.AccountRole_role[role_id]
        )
        account_query = select(PostgresModels.Account).where(
            and_(
                or_(
                    PostgresModels.Account.username == data.username_or_email,
                    PostgresModels.Account.email == data.username_or_email,
                ),
                PostgresModels.Account.id_account_role == user_role.id,
            )
        )
        account = self.session.scalars(account_query).first()
        if account is None or not _validate_hash(data.password, account.password):
            return None, "Wrong username or password"
        chat_account = ChatAccountRepository(session=self.session).get_by_account_type(
            account.id, PostgresModels.CONSTANTS.ChatAccount_account_type[0]
        )
        chat_account_id = chat_account.id if chat_account is not None else None
        account_tokens = {
            "access_token": _create_token(account.id, ACCESS_TOKEN_TYPE, chat_account_identifier=chat_account_id),
            "refresh_token": _create_token(account.id, REFRESH_TOKEN_TYPE),
            "token_type": "bearer",
        }
        return account_tokens, None
