from app import create_app
from app.db import db
from app.models import User, Product

app = create_app()
# with app.app_context():
#     db.create_all()  # 모든 테이블 생성

#     # 예시 데이터 삽입
#     user = User(name="John Doe", email="john@example.com")
#     product = Product(name="Sample Product", price=100)

#     db.session.add(user)
#     db.session.add(product)
#     db.session.commit()
