# app/db/seed.py
from app import create_app
from app.db import Session  # sessionmaker로 생성된 세션 가져오기
from app.models.user_model import User

def seed_data():
    session = Session()  # 세션을 직접 생성
    try:
        # 기본 사용자 데이터
        user1 = User(name="Alice", email="alice@example.com", password="hashed_password_1")
        user2 = User(name="Bob", email="bob@example.com", password="hashed_password_2")

        session.add_all([user1, user2])
        session.commit()
        print("Seed data inserted successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting seed data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():  # 애플리케이션 컨텍스트 내에서 실행
        seed_data()