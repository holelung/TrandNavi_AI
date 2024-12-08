# app/models/user_model.py
from datetime import datetime
from sqlalchemy import ForeignKey, String, Integer, DateTime, Column
from sqlalchemy.orm import relationship

from app.models.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # User:Cart 1:N
    cart_items = relationship('Cart', back_populates='user')
     # Message 관계 추가
    messages = relationship("Message", back_populates="user")


    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
    
    def __repr__(self) -> str: 
        return f"<User(id={self.id!r}, name={self.name!r}, email={self.email!r},)>"