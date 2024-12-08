from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    
    room_id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Message와의 관계 정의
    messages = relationship("Message", back_populates="chat_room")

    def __init__(self, room_name):
        self.room_name = room_name

    def __repr__(self) -> str:
        return f"<ChatRoom(room_id={self.room_id}, room_name={self.room_name})>"