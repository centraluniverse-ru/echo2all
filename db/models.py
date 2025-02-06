from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    role = Column(String, default="user")
    is_banned_bot = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    is_receiving = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.now)
    joined_at = Column(DateTime, default=datetime.now)
    is_verified = Column(Boolean, default=False)
    ban_reason = Column(String, nullable=True)
    warn_count = Column(Integer, default=0)
    sign = Column(String, nullable=True)  # Новое поле подписи

    def __repr__(self):
        return (
            f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username}, "
            f"role={self.role}, is_banned_bot={self.is_banned_bot}, is_receiving={self.is_receiving}, "
            f"message_count={self.message_count}, last_activity={self.last_activity}, "
            f"joined_at={self.joined_at}, is_verified={self.is_verified}, "
            f"ban_reason={self.ban_reason}, warn_count={self.warn_count}, sign={self.sign})>"
        )

