from flask import Blueprint, jsonify
from models.category import MainCategory, SubCategory

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
def get_all_categories():
    """獲取所有產品分類（階層結構）"""
    try:
        main_categories = MainCategory.all()
        result = []

        for main_cat in main_categories:
            sub_cats = SubCategory.filter_by(main_category_id=main_cat.id)

            category_data = {
                'id': main_cat.id,
                'name': main_cat.name,
                'description': main_cat.description,
                'subcategories': [
                    {
                        'id': sub_cat.id,
                        'name': sub_cat.name,
                        'description': sub_cat.description
                    } for sub_cat in sub_cats
                ]
            }
            result.append(category_data)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"獲取分類失敗: {str(e)}"}), 500

@categories_bp.route('/main', methods=['GET'])
def get_main_categories():
    """獲取所有主分類"""
    try:
        main_categories = MainCategory.all()
        result = [
            {
                'id': cat.id,
                'name': cat.name,
                'description': cat.description
            } for cat in main_categories
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"獲取主分類失敗: {str(e)}"}), 500

@categories_bp.route('/main/<main_id>/subcategories', methods=['GET'])
def get_subcategories(main_id):
    """獲取指定主分類下的所有子分類"""
    try:
        subcategories = SubCategory.filter_by(main_category_id=str(main_id))
        result = [
            {
                'id': cat.id,
                'name': cat.name,
                'description': cat.description,
                'main_category_id': cat.main_category_id
            } for cat in subcategories
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"獲取子分類失敗: {str(e)}"}), 500