# app/routes/cart_routes.py
from flask import Blueprint, request, jsonify
from app.db import Session
from app.models.cart_model import Cart
from app.models.user_model import User

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import verify_jwt_in_request

cart_bp = Blueprint('cart', __name__)

# 장바구니에 상품추가
@cart_bp.route('/cart', methods=['POST'])
def add_to_cart():
    verify_jwt_in_request()
    
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    product_name = data.get('product_name')
    product_detail = data.get('product_detail')
    product_img = data.get('product_img')
    price = data.get('price')
    product_url = data.get('product_url')
    
    session = Session()
    new_cart_item = Cart(
        product_name=product_name,
        product_detail=product_detail, 
        product_img=product_img, 
        price=price,
        product_url=product_url
    )
    new_cart_item.user_id = user_id
    session.add(new_cart_item)
    session.commit()
    session.close()
    
    return jsonify({"message": "Item add to cart"}), 201


# 장바구니에서 항목 제거
@cart_bp.route('/cart/<int:cart_id>',methods=['DELETE'])
@jwt_required()
def remove_from_cart(cart_id):
    user_id = get_jwt_identity()
    session = Session()
    
    # 해당 항목이 장바구니에 있는지 확인 후 삭제
    cart_item = session.query(Cart).filter_by(id=cart_id, user_id=user_id).first()
    if not cart_item:
        session.close()
        return jsonify({"error":"Item not found in your cart"}), 404
    
    session.delete(cart_item)
    session.commit()
    session.close
    
    return jsonify({"message":"Item removed from cart"}), 200

    


# 상품 목록 불러오기
@cart_bp.route('/cart_load', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    session = Session()
    
    # 장바구니 항목 조회
    cart_items = session.query(Cart).filter_by(user_id=user_id).all()
    session.close()
    
    # 각 항목을 JSON으로 변환
    cart_items_list = [
        {
            "id": item.id,
            "product_name": item.product_name,
            "product_detail": item.product_detail,
            "product_img": item.product_img,
            "price": float(item.price),
            "add_at": item.add_at
        }
        for item in cart_items
    ]
    return jsonify(cart_items_list), 200