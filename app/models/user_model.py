from . import db
from datetime import datetime
from sqlalchemy import ForeignKey, String, Integer, DateTime, Column
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # User:Cart 1:N
    cart_items = relationship('Cart', back_populates='user')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column()

    def __repr__(self):
        return f"<User {self.name}>"
