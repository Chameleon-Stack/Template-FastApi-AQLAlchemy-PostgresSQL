from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from kanban.database import db


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    password: Mapped[str]
    email: Mapped[str]
    photo: Mapped[Optional[str]]
    create_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now()
    )
    update_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now()
    )
    cards: Mapped[List['Card']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )
    cards_categories: Mapped[List['CardCategory']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )

    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return False

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return str(self.id)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'password': self.password,
            'email': self.email,
            'photo': self.photo,
            'create_at': self.create_at.isoformat(),
            'update_at': self.update_at.isoformat(),
            'cards': [card.to_dict() for card in self.cards],
        }


class Card(Base):
    __tablename__ = 'cards'
    id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str]
    title: Mapped[str]
    description: Mapped[Optional[str]]
    create_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now()
    )
    update_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now()
    )
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='cards')
    category_id: Mapped[int] = mapped_column(ForeignKey('cards_categories.id'))
    category: Mapped['CardCategory'] = relationship(back_populates='card')

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'title': self.title,
            'description': self.description,
            'create_at': self.create_at.isoformat(),
            'update_at': self.update_at.isoformat(),
            'user_id': self.user_id,
            'category_id': self.category_id,
        }


class CardCategory(Base):
    __tablename__ = 'cards_categories'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    color: Mapped[str]
    create_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now()
    )
    update_at: Mapped[Optional[datetime]] = mapped_column(
        default=datetime.now()
    )
    card: Mapped['Card'] = relationship(
        back_populates='category', cascade='all, delete-orphan'
    )
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='cards_categories')

    def to_dict(self):
        if self.card:
            card_id = self.card.id
        else:
            card_id = None
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'create_at': self.create_at.isoformat(),
            'update_at': self.update_at.isoformat(),
            'card_id': card_id,
        }


Base.metadata.create_all(db)
