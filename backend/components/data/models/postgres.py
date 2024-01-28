from datetime import datetime
from typing import Annotated, Optional, List
from sqlalchemy import ForeignKey, types, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, MappedAsDataclass

str64 = Annotated[str, None]
str256 = Annotated[str, None]

int_PK = Annotated[int, mapped_column(primary_key=True)]
smallint = Annotated[int, None]
timestamp = Annotated[datetime, mapped_column(default=datetime.utcnow)]


class Base(DeclarativeBase):
    type_annotation_map = {
        str64: types.VARCHAR(64),
        str256: types.VARCHAR(256),
        smallint: types.SMALLINT,
        timestamp: types.TIMESTAMP,
    }


class Account(Base):
    """Store account's credential info. Used for validating access to application \n
   Primary key: id \n
   Foreign key: accountinfo_id -> Accountinfo"""

    __tablename__ = 'account'
    id: Mapped[int_PK]
    username: Mapped[str64]  # Mapped without Optional[] is set to nullable = False
    password: Mapped[str64]
    email: Mapped[str64]
    name: Mapped[str64]
    time_created: Mapped[timestamp]
