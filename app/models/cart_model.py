# app/models/user_model.py
from datetime import datetime
from sqlalchemy import ForeignKey, String, Integer, DateTime, Column, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON

from app.models.base import Base

class Cart(Base):
    __tablename__ = "cart"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_name = Column(String(100), nullable=False)
    product_detail = Column(JSON, nullable=True)
    price = Column(Numeric(15, 2), nullable=True)
    product_img = Column(String(200), nullable=True)
    product_url = Column(String(200), nullable=True)
    add_at = Column(DateTime, default=datetime.now)
    
    # User relationship
    user = relationship('User', back_populates='cart_items')
    
    def __init__(self, product_name, product_detail, product_img, price, product_url):
        self.product_name = product_name
        self.product_detail = product_detail
        self.product_img = product_img
        self.price = price
        self.product_url = product_url
        
    def __repr__(self) -> str:
        return f"<Cart(id={self.id!r}, user_id={self.user_id!r}, product_name={self.product_name!r}, product_detail={self.product_detail!r}, product_img={self.product_img}, price={self.price!r}, product_url={self.product_url!r})>"
    
    