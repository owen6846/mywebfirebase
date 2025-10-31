from flask_jwt_extended import JWTManager
from flask import current_app

jwt = JWTManager()

def get_db():
    """取得 Firestore 客戶端"""
    return current_app.db

# 導入所有模型
from .user import User
from .category import MainCategory, SubCategory
from .product import Product, ProductImage
from .document import Document
from .carousel import Carousel