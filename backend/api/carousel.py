from flask import Blueprint, jsonify, redirect
from models.carousel import Carousel

carousel_bp = Blueprint('carousel', __name__)

@carousel_bp.route('/', methods=['GET'])
def get_carousel_items():
    """獲取所有啟用的輪播圖項目"""
    try:
        # Firebase 查詢並排序
        all_carousels = Carousel.filter_by(is_active=True)
        # 手動排序
        carousel_items = sorted(all_carousels, key=lambda x: x.order_num)

        result = []

        for item in carousel_items:
            carousel_data = {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'image_url': item.image_url,
                'link_url': item.link_url,
                'order_num': item.order_num
            }
            result.append(carousel_data)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"獲取輪播圖失敗: {str(e)}"}), 500

@carousel_bp.route('/image/<carousel_id>', methods=['GET'])
def get_carousel_image(carousel_id):
    """獲取輪播圖圖片 - 重定向到 Storage URL"""
    try:
        carousel = Carousel.get(carousel_id)
        if not carousel:
            return jsonify({"error": "找不到輪播圖"}), 404

        # 直接重定向到 Firebase Storage URL
        return redirect(carousel.image_url)
    except Exception as e:
        return jsonify({"error": f"獲取輪播圖圖片失敗: {str(e)}"}), 500