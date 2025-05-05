from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):  # type: ignore[misc, valid-type]
    __tablename__ = "user"
    full_name = Column(String, nullable=True)
