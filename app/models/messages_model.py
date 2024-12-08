    # CREATE TABLE messages (
    #   message_id INT PRIMARY KEY AUTO_INCREMENT,
    #   room_id INT,
    #   user_id INT,
    #   content TEXT,
    #   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    #   FOREIGN KEY (room_id) REFERENCES chat_rooms(room_id),
    #   FOREIGN KEY (user_id) REFERENCES users(user_id)
    # );