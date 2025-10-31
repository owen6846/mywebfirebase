from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from models.user import User
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用戶登入"""
    try:
        if not request.is_json:
            return jsonify({"error": "缺少JSON資料"}), 400

        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username or not password:
            return jsonify({"error": "缺少使用者名稱或密碼"}), 400

        # Firebase 查詢
        user = User.filter_by(username=username)

        if not user:
            return jsonify({"error": "使用者名稱或密碼錯誤"}), 401

        if not user.check_password(password):
            return jsonify({"error": "使用者名稱或密碼錯誤"}), 401

        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200

    except Exception as e:
        return jsonify({"error": f"伺服器錯誤: {str(e)}"}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    """獲取當前用戶資料"""
    try:
        user_id = get_jwt_identity()
        user = User.get(user_id)

        if not user:
            return jsonify({"error": "用戶不存在"}), 404

        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 200
    except Exception as e:
        return jsonify({"error": f"獲取用戶資料失敗: {str(e)}"}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密碼"""
    try:
        user_id = get_jwt_identity()
        user = User.get(user_id)

        if not user:
            return jsonify({"error": "用戶不存在"}), 404

        data = request.json
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return jsonify({"error": "缺少舊密碼或新密碼"}), 400

        if not user.check_password(old_password):
            return jsonify({"error": "舊密碼錯誤"}), 400

        user.password_hash = generate_password_hash(new_password)

        if user.save():
            return jsonify({"message": "密碼已成功修改"}), 200
        else:
            return jsonify({"error": "密碼修改失敗"}), 500

    except Exception as e:
        return jsonify({"error": f"修改密碼失敗: {str(e)}"}), 500