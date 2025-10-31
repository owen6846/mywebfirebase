from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify
from models.user import User

def admin_required():
    """檢查是否為管理員的裝飾器"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.get(user_id)

            if not user or not user.is_admin:
                return jsonify({"error": "Admin privilege required"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper

def get_current_user():
    """獲取當前登入的用戶"""
    user_id = get_jwt_identity()
    return User.get(user_id)