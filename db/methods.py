from db.models import User
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import uuid


class UserCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, telegram_id: int, username: Optional[str] = None, role: str = "user") -> User:
        user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            return user
        new_user = User(
            id=str(uuid.uuid4()),
            telegram_id=telegram_id,
            username=username,
            role=role
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def create_user(self, telegram_id: int, username: Optional[str] = None, role: str = "user") -> User:
        user = User(
            id=str(uuid.uuid4()), telegram_id=telegram_id, username=username, role=role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()
    
    def get_users_for_echo(self) -> List[User]:
        return self.db.query(User).filter(User.is_receiving == True, User.role != "admin").all()
    
    def get_admins(self) -> List[User]:
        return self.db.query(User).filter(User.role == "admin").all()
    
    def count_users(self) -> dict:
        total_users = self.db.query(User).count()
        banned_bot_users = self.db.query(User).filter(User.is_banned_bot == True).count()
        receiving_messages_users = self.db.query(User).filter(User.is_receiving == True).count()
        return {
            "total_users": total_users,
            "banned_bot_users": banned_bot_users,
            "receiving_messages_users": receiving_messages_users
        }

    def update_user(self, telegram_id: int, **kwargs) -> Optional[User]:
        user = self.get_or_create_user(telegram_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_user(self, telegram_id: int) -> bool:
        user = self.get_or_create_user(telegram_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def increment_message_count(self, telegram_id: int) -> Optional[User]:
        user = self.get_or_create_user(telegram_id)
        if user:
            user.message_count += 1
            self.db.commit()
            self.db.refresh(user)
        return user

    def add_warn(self, user_id: str) -> Optional[User]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.warn_count += 1
            self.db.commit()
            self.db.refresh(user)
        return user

    def ban_user(self, user_id: str, reason: Optional[str] = None) -> Optional[User]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_banned = True
            user.ban_reason = reason
            self.db.commit()
            self.db.refresh(user)
        return user

    def unban_user(self, telegram_id: int) -> Optional[User]:
        user = self.get_or_create_user(telegram_id)
        if user:
            user.is_banned = False
            user.ban_reason = None
            self.db.commit()
            self.db.refresh(user)
        return user

    def set_is_banned_bot(self, telegram_id: int, is_banned: bool) -> Optional[User]:
        user = self.get_or_create_user(telegram_id)
        if user:
            user.is_banned_bot = is_banned
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def update_sign(self, telegram_id: int, sign: str) -> Optional[User]:
        user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            user.sign = sign
            self.db.commit()
            self.db.refresh(user)
        return user

