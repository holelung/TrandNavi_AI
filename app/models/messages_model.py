
# app/models/messages_model.py
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.room_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # ChatRoom와의 관계 정의
    chat_room = relationship("ChatRoom", back_populates="messages")
    user = relationship("User", back_populates="messages")

    def __init__(self, room_id, user_id, content):
        self.room_id = room_id
        self.user_id = user_id
        self.content = content

    def __repr__(self) -> str:
        return f"<Message(message_id={self.message_id}, room_id={self.room_id}, user_id={self.user_id}, content={self.content})>"

