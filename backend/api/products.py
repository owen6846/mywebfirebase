from flask import Blueprint, jsonify, request, redirect
from models.product import Product, ProductImage
from models.category import MainCategory, SubCategory

products_bp = Blueprint('products', __name__)

@products_bp.route('/featured', methods=['GET'])
def get_featured_products():
    """獲取特色產品（最多6個）"""
    try:
        # Firebase 查詢
        featured_products = Product.filter_by(is_featured=True)
        featured_products = featured_products[:6]  # 限制6個

        result = []

        for product in featured_products:
            # 獲取主圖片
            images = ProductImage.filter_by(product_id=product.id, is_main=True)
            main_image = images[0] if images else None

            # 如果沒有主圖片，使用第一張圖片
            if not main_image:
                all_images = ProductImage.filter_by(product_id=product.id)
                main_image = all_images[0] if all_images else None

            # 獲取子分類和主分類
            sub_category = SubCategory.get(product.sub_category_id)
            main_category = None
            if sub_category:
                main_category = MainCategory.get(sub_category.main_category_id)

            # 組裝產品數據
            product_data = {
                'id': product.id,
                'name': product.name,
                'model': product.model,
                'price': float(product.price) if product.price else None,
                'description': product.description,
                'has_image': main_image is not None,
                'image_id': main_image.id if main_image else None,
                'image_url': main_image.image_url if main_image else None,
                'sub_category_id': product.sub_category_id,
                'sub_category_name': sub_category.name if sub_category else None,
                'main_category_id': main_category.id if main_category else None,
                'main_category_name': main_category.name if main_category else None
            }
            result.append(product_data)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"獲取特色產品失敗: {str(e)}"}), 500

@products_bp.route('/category/main/<main_id>', methods=['GET'])
def get_products_by_main_category(main_id):
    """獲取指定主分類下的所有產品"""
    try:
        # 獲取該主分類下所有子分類的ID
        sub_categories = SubCategory.filter_by(main_category_id=str(main_id))
        sub_category_ids = [sub.id for sub in sub_categories]

        if not sub_category_ids:
            return jsonify([]), 200

        # 獲取這些子分類下的所有產品
        products = Product.filter_by_subcategories(sub_category_ids)
        result = []

        for product in products:
            # 獲取主圖片
            images = ProductImage.filter_by(product_id=product.id, is_main=True)
            main_image = images[0] if images else None

            # 如果沒有主圖片，使用第一張圖片
            if not main_image:
                all_images = ProductImage.filter_by(product_id=product.id)
                main_image = all_images[0] if all_images else None

            # 獲取子分類
            sub_category = SubCategory.get(product.sub_category_id)

            # 組裝產品數據
            product_data = {
                'id': product.id,
                'name': product.name,
                'model': product.model,
                'price': float(product.price) if product.price else None,
                'description': product.description,
                'has_image': main_image is not None,
                'image_id': main_image.id if main_image else None,
                'image_url': main_image.image_url if main_image else None,
                'sub_category_id': product.sub_category_id,
                'sub_category_name': sub_category.name if sub_category else None
            }
            result.append(product_data)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"獲取產品失敗: {str(e)}"}), 500

@products_bp.route('/category/sub/<sub_id>', methods=['GET'])
def get_products_by_sub_category(sub_id):
    """獲取指定子分類下的所有產品"""
    try:
        products = Product.filter_by(sub_category_id=str(sub_id))
        result = []

        for product in products:
            # 獲取主圖片
            images = ProductImage.filter_by(product_id=product.id, is_main=True)
            main_image = images[0] if images else None

            # 如果沒有主圖片，使用第一張圖片
            if not main_image:
                all_images = ProductImage.filter_by(product_id=product.id)
                main_image = all_images[0] if all_images else None

            # 組裝產品數據
            product_data = {
                'id': product.id,
                'name': product.name,
                'model': product.model,
                'price': float(product.price) if product.price else None,
                'description': product.description,
                'has_image': main_image is not None,
                'image_id': main_image.id if main_image else None,
                'image_url': main_image.image_url if main_image else None
            }
            result.append(product_data)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"獲取產品失敗: {str(e)}"}), 500

@products_bp.route('/<product_id>', methods=['GET'])
def get_product_detail(product_id):
    """獲取產品詳細信息"""
    try:
        product = Product.get(product_id)
        if not product:
            return jsonify({"error": "找不到產品"}), 404

        # 獲取產品圖片
        product_images = ProductImage.filter_by(product_id=product.id)
        images_data = [
            {
                'id': img.id,
                'url': img.image_url,
                'is_main': img.is_main
            } for img in product_images
        ]

        # 獲取子分類和主分類
        sub_category = SubCategory.get(product.sub_category_id)
        main_category = None
        if sub_category:
            main_category = MainCategory.get(sub_category.main_category_id)

        # 組裝產品詳細數據
        product_detail = {
            'id': product.id,
            'name': product.name,
            'model': product.model,
            'price': float(product.price) if product.price else None,
            'description': product.description,
            'specifications': product.specifications,
            'sub_category_id': product.sub_category_id,
            'sub_category_name': sub_category.name if sub_category else None,
            'main_category_id': main_category.id if main_category else None,
            'main_category_name': main_category.name if main_category else None,
            'images': images_data
        }

        return jsonify(product_detail), 200
    except Exception as e:
        return jsonify({"error": f"獲取產品詳細信息失敗: {str(e)}"}), 500

@products_bp.route('/image/<image_id>', methods=['GET'])
def get_product_image(image_id):
    """獲取產品圖片 - 重定向到 Storage URL"""
    try:
        image = ProductImage.get(image_id)
        if not image:
            return jsonify({"error": "找不到圖片"}), 404

        # 直接重定向到 Firebase Storage URL
        return redirect(image.image_url)
    except Exception as e:
        return jsonify({"error": f"獲取產品圖片失敗: {str(e)}"}), 500

@products_bp.route('/search', methods=['GET'])
def search_products():
    """搜尋產品"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([]), 200

        # Firebase 搜尋
        products = Product.search(query)

        result = []
        for product in products:
            # 獲取主圖片
            images = ProductImage.filter_by(product_id=product.id, is_main=True)
            main_image = images[0] if images else None

            # 如果沒有主圖片，使用第一張圖片
            if not main_image:
                all_images = ProductImage.filter_by(product_id=product.id)
                main_image = all_images[0] if all_images else None

            # 獲取子分類
            sub_category = SubCategory.get(product.sub_category_id)

            # 組裝產品數據
            product_data = {
                'id': product.id,
                'name': product.name,
                'model': product.model,
                'price': float(product.price) if product.price else None,
                'description': product.description,
                'has_image': main_image is not None,
                'image_id': main_image.id if main_image else None,
                'image_url': main_image.image_url if main_image else None,
                'sub_category_id': product.sub_category_id,
                'sub_category_name': sub_category.name if sub_category else None
            }
            result.append(product_data)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"搜尋產品失敗: {str(e)}"}), 500