from datetime import datetime
from typing import Annotated, Optional, List, Any
from sqlalchemy import ForeignKey, Table, Column, Integer, Text, VARCHAR, SMALLINT, TIMESTAMP, ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

str16 = Annotated[str, mapped_column(VARCHAR(16))]
str64 = Annotated[str, mapped_column(VARCHAR(64))]
str256 = Annotated[str, mapped_column(VARCHAR(256))]

int_PK = Annotated[int, mapped_column(primary_key=True)]
smallint = Annotated[int, mapped_column(SMALLINT)]
timestamp = Annotated[datetime, mapped_column(TIMESTAMP, default=datetime.utcnow)]
str_array = Annotated[List[str], mapped_column(ARRAY(VARCHAR(64)))]


class Base(DeclarativeBase):
    type_annotation_map = {
        str: Text,
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

    id_account_role: Mapped[int] = Column(Integer, ForeignKey('account_role.id'))
    rel_account_role: Mapped['AccountRole'] = relationship('AccountRole', back_populates='rel_accounts')

    id_visitor: Mapped[Optional[int]] = Column(Integer, ForeignKey('visitor.id'))
    rel_visitor: Mapped[Optional['Visitor']] = relationship('Visitor')

    rel_scenarios: Mapped[List['Scenario']] = relationship('Scenario', back_populates='rel_account')
    rel_businesses: Mapped[List['Business']] = relationship('Business', back_populates='rel_account')
    rel_bots: Mapped[List['Bot']] = relationship('Bot', back_populates='rel_account')


class AccountRole(Base):
    """Store account's role info. Used for validating access to application \n
   Primary key: id \n
   Foreign key: id_account -> Account"""

    __tablename__ = 'account_role'
    id: Mapped[int_PK]
    role: Mapped[str64]

    rel_accounts: Mapped[List[Account]] = relationship('Account', back_populates='rel_account_role', uselist=True)


class Visitor(Base):
    """Store chat visitor information. \n"""

    __tablename__ = 'visitor'
    id: Mapped[int_PK]
    visitor_type: Mapped[str16]
    visitor_id: Mapped[int]
    name: Mapped[Optional[str64]]
    time_created: Mapped[timestamp]


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

    id_account: Mapped[int] = Column(Integer, ForeignKey('account.id'))
    rel_account: Mapped[Account] = relationship('Account', back_populates='rel_businesses')

    rel_business_products: Mapped[List['BusinessProduct']] = relationship('BusinessProduct', back_populates='rel_business')
    rel_scenarios: Mapped[List['Scenario']] = relationship('Scenario', back_populates='rel_business')


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

    id_business: Mapped[int] = Column(Integer, ForeignKey('business.id'))
    rel_business: Mapped[Business] = relationship('Business', back_populates='rel_business_products')


class Bot(Base):
    """Store bot information \n
   Primary key: id \n
   Foreign key: id_business -> Business"""

    __tablename__ = 'bot'
    id: Mapped[int_PK]
    name: Mapped[str64]
    description: Mapped[str]
    model_name: Mapped[str64]
    prompt: Mapped[str]
    prompt_tools: Mapped[str_array]
    time_created: Mapped[timestamp]

    id_account: Mapped[int] = Column(Integer, ForeignKey('account.id'))
    rel_account: Mapped[Account] = relationship('Account', back_populates='rel_bots')


class Scenario(Base):
    """Store chat process information \n
   Primary key: id \n"""

    __tablename__ = 'scenario'
    id: Mapped[int_PK]
    name: Mapped[str64]
    time_created: Mapped[timestamp]
    flow: Mapped[dict[str, Any]]

    id_account: Mapped[int] = Column(Integer, ForeignKey('account.id'))
    rel_account: Mapped[Account] = relationship('Account', back_populates='rel_scenarios')

    id_business: Mapped[int] = Column(Integer, ForeignKey('business.id'))
    rel_business: Mapped[Business] = relationship('Business', back_populates='rel_scenarios')

    id_bot: Mapped[int] = Column(Integer, ForeignKey('bot.id'))
    # rel_bot: Mapped[Bot] = relationship('Bot', back_populates='rel_scenarios')


class ChatSession(Base):
    """Store chat information \n
   Primary key: id \n
   Foreign key: id_scenario -> Scenario"""

    __tablename__ = 'chat_session'
    id: Mapped[int_PK]
    account_type: Mapped[str16]
    time_created: Mapped[timestamp]

    id_visitor: Mapped[int] = Column(Integer, ForeignKey('visitor.id'))

    # id_scenario: Mapped[int] = Column(Integer, ForeignKey('scenario.id'))
    # rel_scenario: Mapped[Scenario] = relationship('Scenario', back_populates='rel_chats')

    id_bot: Mapped[int] = Column(Integer, ForeignKey('bot.id'))
    # rel_bot: Mapped[Bot] = relationship('Bot', back_populates='rel_chats')


class ChatMessage(Base):
    """Store chat message information \n
   Primary key: id \n
   Foreign key: id_chat -> Chat"""

    __tablename__ = 'chat_message'
    id: Mapped[int_PK]
    message: Mapped[str]
    time_created: Mapped[timestamp]

    id_chat: Mapped[int] = Column(Integer, ForeignKey('chat.id'))
    # rel_chat: Mapped[Chat] = relationship('Chat', back_populates='rel_messages')
