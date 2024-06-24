from datetime import datetime, timezone
from typing import Annotated, Optional, List, Any
from sqlalchemy import ForeignKey, Column, INTEGER, TEXT, VARCHAR, SMALLINT, TIMESTAMP, ARRAY, JSON, BIGINT, FLOAT, BOOLEAN
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from configurations.envs import ChatModels


def aware_utcnow():
    # datetime.utcnow() is deprecated
    return datetime.now(timezone.utc)


str16 = Annotated[str, mapped_column(VARCHAR(16))]
str32 = Annotated[str, mapped_column(VARCHAR(32))]
str64 = Annotated[str, mapped_column(VARCHAR(64))]
str256 = Annotated[str, mapped_column(VARCHAR(256))]

int_PK = Annotated[int, mapped_column(primary_key=True)]
smallint = Annotated[int, mapped_column(SMALLINT)]
bigint = Annotated[int, mapped_column(BIGINT)]
timestamp = Annotated[datetime, mapped_column(TIMESTAMP, default=aware_utcnow)]
str_array = Annotated[List[str], mapped_column(ARRAY(VARCHAR(64)))]


class CONSTANTS:
    AccountRole_role = ['Admin', 'User']
    ChatAccount_account_type = ['internal', 'facebook', 'zalo']
    ChatMessage_type = ['bot', 'bot-form', 'admin', 'user-text', 'user-options']


class Base(DeclarativeBase):
    type_annotation_map = {
        str: TEXT,
        dict[str, Any]: JSON,
    }


class Account(Base):
    """Store account's credential info. Used for validating access to application \n
   Primary key: id \n
   Foreign key: accountinfo_id -> Accountinfo"""

    __tablename__ = 'account'
    id: Mapped[int_PK]
    username: Mapped[str64]  # Mapped without Optional[] is set to nullable = False
    password: Mapped[str256]
    email: Mapped[str64]
    name: Mapped[str64]
    time_created: Mapped[timestamp]

    id_account_role: Mapped[int] = Column(INTEGER, ForeignKey('account_role.id'))
    rel_account_role: Mapped['AccountRole'] = relationship('AccountRole', back_populates='rel_accounts')

    # id_chat_account: Mapped[[int]] = Column(INTEGER, ForeignKey('chat_account.id'))
    # rel_chat_account: Mapped[['ChatAccount']] = relationship('ChatAccount')

    rel_scenarios: Mapped[List['Scenario']] = relationship('Scenario', back_populates='rel_account', uselist=True)
    rel_businesses: Mapped[List['Business']] = relationship('Business', back_populates='rel_account', uselist=True)
    rel_bots: Mapped[List['Bot']] = relationship('Bot', back_populates='rel_account', uselist=True, cascade="all, delete-orphan")


class AccountRole(Base):
    """Store account's role info. Used for validating access to application \n
   Primary key: id \n
   Foreign key: id_account -> Account"""

    __tablename__ = 'account_role'
    id: Mapped[int_PK]
    role: Mapped[str16]  # admin / user

    rel_accounts: Mapped[List[Account]] = relationship('Account', back_populates='rel_account_role', uselist=True)


class Business(Base):
    """Store business information \n
   Primary key: id \n
   Foreign key: id_account -> Account"""

    __tablename__ = 'business'
    id: Mapped[int_PK]
    name: Mapped[str64]
    description: Mapped[str]
    fields: Mapped[str_array]
    address: Mapped[Optional[str256]]
    phone: Mapped[Optional[str16]]
    website_url: Mapped[Optional[str64]]
    time_created: Mapped[timestamp]

    id_account: Mapped[int] = Column(INTEGER, ForeignKey('account.id'))
    rel_account: Mapped[Account] = relationship('Account', back_populates='rel_businesses')

    rel_business_products: Mapped[List['BusinessProduct']] = relationship('BusinessProduct', back_populates='rel_business', uselist=True)
    rel_scenarios: Mapped[List['Scenario']] = relationship('Scenario', back_populates='rel_business', uselist=True)


# class BusinessAdmin(Base):
#     """Store business admin information \n
#    Primary key: id \n
#    Foreign key: id_business -> Business"""
#
#     __tablename__ = 'business_admin'
#     id: Mapped[int_PK]
#     admin_type: Mapped[str16]
#     id_business: Mapped[int]
#     id_account: Mapped[int]
#     time_created: Mapped[timestamp]
#
#     rel_business: Mapped[Business] = relationship('Business')
#     rel_account: Mapped[Account] = relationship('Account')


class BusinessField(Base):
    """Store business field information\n"""

    __tablename__ = 'business_field'
    id: Mapped[int_PK]
    field: Mapped[str64]


class BusinessProduct(Base):
    """Store business product information \n
   Primary key: id \n
   Foreign key: id_business -> Business"""

    __tablename__ = 'business_product'
    id: Mapped[int_PK]
    name: Mapped[str64]
    description: Mapped[str]
    price: Mapped[int]
    url: Mapped[Optional[str256]]
    time_created: Mapped[timestamp]

    id_business: Mapped[int] = Column(INTEGER, ForeignKey('business.id'))
    rel_business: Mapped[Business] = relationship('Business', back_populates='rel_business_products')


class Bot(Base):
    """Store bot information"""

    __tablename__ = 'bot'
    id: Mapped[int_PK]
    name: Mapped[str64]
    description: Mapped[str]
    is_public: Mapped[bool] = Column(BOOLEAN, default=False)
    conf_model_temperature: Mapped[float] = Column(FLOAT, default=0.5)
    conf_model_name: Mapped[str64]
    conf_instruction: Mapped[str]
    conf_external_data: Mapped[Optional[str]]
    time_created: Mapped[timestamp]

    id_account: Mapped[int] = Column(INTEGER, ForeignKey('account.id'))
    rel_account: Mapped[Account] = relationship('Account', back_populates='rel_bots')

    rel_bot_context: Mapped[List['BotContext']] = relationship('BotContext', back_populates='rel_bot', uselist=True, cascade="all, delete-orphan")


# class BotModel(Base):
#     """Store bot model information \n
#    Primary key: id \n"""
#
#     __tablename__ = 'bot_model'
#     id: Mapped[int_PK]
#     name: Mapped[str64]

class BotContext(Base):
    """Store bot context information \n"""

    __tablename__ = 'bot_context'
    id: Mapped[int_PK]
    filename: Mapped[str64]
    description: Mapped[Optional[str]]
    embedding_model_used: Mapped[Optional[str64]] = mapped_column(VARCHAR(64), default=ChatModels.DEFAULT_EMBEDDING_MODEL_NAME)
    time_created: Mapped[timestamp]

    id_bot: Mapped[int] = Column(INTEGER, ForeignKey('bot.id'))
    rel_bot: Mapped[Bot] = relationship('Bot')


class Scenario(Base):
    """Store chat process information \n
   Primary key: id \n"""

    __tablename__ = 'scenario'
    id: Mapped[int_PK]
    name: Mapped[str64]
    flow: Mapped[dict[str, Any]]
    time_created: Mapped[timestamp]

    id_account: Mapped[int] = Column(INTEGER, ForeignKey('account.id'))
    rel_account: Mapped[Account] = relationship('Account', back_populates='rel_scenarios')

    id_business: Mapped[int] = Column(INTEGER, ForeignKey('business.id'))
    rel_business: Mapped[Business] = relationship('Business', back_populates='rel_scenarios')

    id_bot: Mapped[int] = Column(INTEGER, ForeignKey('bot.id'))
    # rel_bot: Mapped[Bot] = relationship('Bot', back_populates='rel_scenarios')


class ChatAccount(Base):
    """Store chat account information. \n"""

    __tablename__ = 'chat_account'
    id: Mapped[int_PK]
    account_type: Mapped[str16]  # type of linked account (internal / facebook / zalo / ...)
    name: Mapped[Optional[str64]]
    id_external_account: Mapped[Optional[str64]]  # id of external account
    time_created: Mapped[timestamp]

    id_internal_account: Mapped[Optional[int]] = Column(INTEGER, ForeignKey('account.id'))  # id of linked internal account
    rel_account: Mapped[Optional[Account]] = relationship('Account')


class ChatSession(Base):
    """Store chat information \n"""

    __tablename__ = 'chat_session'
    id: Mapped[int_PK]
    name: Mapped[str64]
    human_reply: Mapped[bool] = Column(BOOLEAN, default=False)  # True if an admin user is replying, False if bot is replying
    time_created: Mapped[timestamp]

    id_chat_account: Mapped[int] = Column(INTEGER, ForeignKey('chat_account.id'))
    rel_chat_account: Mapped[ChatAccount] = relationship('ChatAccount')

    id_bot: Mapped[int] = Column(INTEGER, ForeignKey('bot.id'))
    # rel_bot: Mapped[Bot] = relationship('Bot', back_populates='rel_chats')

    rel_chat_message: Mapped[List['ChatMessage']] = relationship('ChatMessage', back_populates='rel_chat_session', uselist=True)
    # preferred way to run chat session
    # id_scenario: Mapped[int] = Column(INTEGER, ForeignKey('scenario.id'))
    # rel_scenario: Mapped[Scenario] = relationship('Scenario', back_populates='rel_chats')


class ChatMessage(Base):
    """Store chat message information \n
   Primary key: id \n
   Foreign key: id_chat_session -> ChatSession"""

    __tablename__ = 'chat_message'
    id: Mapped[int_PK]
    type: Mapped[str16]  # bot / bot-form / admin / user-text / user-options
    content: Mapped[str]
    time_created: Mapped[timestamp]

    id_chat_session: Mapped[int] = Column(INTEGER, ForeignKey('chat_session.id'))
    rel_chat_session: Mapped[ChatSession] = relationship('ChatSession', back_populates='rel_chat_message')

    id_chat_account: Mapped[Optional[int]] = Column(INTEGER, ForeignKey('chat_account.id'))
    # rel_chat_account: Mapped[ChatAccount] = relationship('ChatAccount')
