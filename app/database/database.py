from sqlalchemy.ext.asyncio import create_async_engine,AsyncAttrs, async_sessionmaker,AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase,declared_attr,relationship
from datetime import datetime
from sqlalchemy import Integer, func,ForeignKey, text
from typing import AsyncGenerator
from enum import Enum
from contextlib import asynccontextmanager
from app.config.config import DB_FOLDER
from app.config.exceptions import Error_DB

DATABASE_URL = f"sqlite+aiosqlite:///{DB_FOLDER}/apidb.db"
# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(
    DATABASE_URL, echo=True
)

# Создаем фабрику сессий для взаимодействия с базой данных
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Создает асинхронную сессию для работы с базой данных"""
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise Error_DB(message=f"Database error: {str(e)}", code=400)
    finally:
        await session.close()



@asynccontextmanager
async def get_db_session():
    """Асинхронный контекстный менеджер для сессии БД"""
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise Error_DB(message=f"Database error: {str(e)}", code=400)
    finally:
        await session.close()


class EventStatus(str, Enum):
    NEW = "NEW"
    FINISHED = "FINISHED"
    IN_PROCESSING = "IN_PROCESSING"


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

class Event(Base):
    group_id : Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    message_text : Mapped[str] = mapped_column(nullable=False)
    message_id: Mapped[str] = mapped_column(nullable=False)
    status_event : Mapped[str] = mapped_column(default=EventStatus.NEW, server_default=text("'NEW'"))

    user: Mapped["User"] = relationship(
        "User", back_populates="events", lazy="selectin", innerjoin=True
    )
    group: Mapped["Group"] = relationship(
        "Group", back_populates="events", lazy="selectin", innerjoin=True
    )


class User(Base):
    firstname: Mapped[str] = mapped_column(nullable=False)
    lastname : Mapped [str]  = mapped_column(nullable=False)
    userid : Mapped [str]  = mapped_column(nullable=False)
    events = relationship(
        "Event", back_populates="user", cascade="all, delete-orphan"
    )

    __mapper_args__ = {"confirm_deleted_rows": False}


class Group(Base):
    chatid: Mapped[str] = mapped_column(nullable=False)
    title : Mapped [str]  = mapped_column(nullable=True)
    type : Mapped[str] = mapped_column(nullable=False)
    events = relationship(
        "Event", back_populates="group", cascade="all, delete-orphan"
    )

    __mapper_args__ = {"confirm_deleted_rows": False}

