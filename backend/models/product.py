from datetime import datetime
from flask import current_app
from firebase_admin import storage
import uuid

class Product:
    """產品模型"""
    COLLECTION = 'products'

    def __init__(self, sub_category_id=None, name=None, model=None,
                 price=None, description=None, specifications=None,
                 is_featured=False, product_id=None):
        self.id = product_id
        self.sub_category_id = sub_category_id
        self.name = name
        self.model = model
        self.price = price
        self.description = description
        self.specifications = specifications
        self.is_featured = is_featured
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def get_db():
        return current_app.db

    @classmethod
    def get(cls, product_id):
        """根據ID獲取產品"""
        if not product_id:
            return None
        db = cls.get_db()
        doc = db.collection(cls.COLLECTION).document(str(product_id)).get()
        if doc.exists:
            return cls._from_doc(doc)
        return None

    @classmethod
    def filter_by(cls, **kwargs):
        """根據條件查詢產品 - 返回列表"""
        db = cls.get_db()
        query = db.collection(cls.COLLECTION)

        for key, value in kwargs.items():
            if key == 'sub_category_id':
                query = query.where(key, '==', str(value))
            else:
                query = query.where(key, '==', value)

        docs = query.stream()
        return [cls._from_doc(doc) for doc in docs]

    @classmethod
    def filter_by_subcategories(cls, sub_category_ids):
        """根據多個子分類ID查詢產品"""
        db = cls.get_db()
        # Firestore 的 in 查詢限制為10個元素
        str_ids = [str(sid) for sid in sub_category_ids]

        if not str_ids:
            return []

        products = []
        # 分批查詢,每批最多10個
        for i in range(0, len(str_ids), 10):
            batch = str_ids[i:i+10]
            query = db.collection(cls.COLLECTION).where('sub_category_id', 'in', batch)
            docs = query.stream()
            products.extend([cls._from_doc(doc) for doc in docs])

        return products

    @classmethod
    def search(cls, search_query):
        """搜尋產品 - 注意: Firestore 不支持 LIKE 查詢,需要全文檢索"""
        # 這是簡化版本,實際應用建議使用 Algolia 或 Elasticsearch
        db = cls.get_db()
        all_docs = db.collection(cls.COLLECTION).stream()

        results = []
        search_lower = search_query.lower()

        for doc in all_docs:
            data = doc.to_dict()
            # 檢查 name, model, description 是否包含搜尋關鍵字
            if (search_lower in str(data.get('name', '')).lower() or
                search_lower in str(data.get('model', '')).lower() or
                search_lower in str(data.get('description', '')).lower()):
                results.append(cls._from_doc(doc))

        return results

    @classmethod
    def limit(cls, limit_num):
        """限制查詢結果數量"""
        db = cls.get_db()
        docs = db.collection(cls.COLLECTION).limit(limit_num).stream()
        return [cls._from_doc(doc) for doc in docs]

    @classmethod
    def _from_doc(cls, doc):
        """從 Firestore 文檔創建對象"""
        data = doc.to_dict()
        obj = cls.__new__(cls)
        obj.id = doc.id
        obj.sub_category_id = data.get('sub_category_id')
        obj.name = data.get('name')
        obj.model = data.get('model')
        obj.price = float(data.get('price', 0)) if data.get('price') else None
        obj.description = data.get('description')
        obj.specifications = data.get('specifications')
        obj.is_featured = data.get('is_featured', False)
        obj.created_at = data.get('created_at')
        obj.updated_at = data.get('updated_at')
        return obj

    def save(self):
        """儲存產品"""
        try:
            db = self.get_db()
            data = {
                'sub_category_id': str(self.sub_category_id),
                'name': self.name,
                'model': self.model,
                'price': float(self.price) if self.price else None,
                'description': self.description,
                'specifications': self.specifications,
                'is_featured': self.is_featured,
                'updated_at': datetime.utcnow()
            }

            if self.id:
                db.collection(self.COLLECTION).document(str(self.id)).update(data)
            else:
                data['created_at'] = self.created_at
                _, doc_ref = db.collection(self.COLLECTION).add(data)
                self.id = doc_ref.id

            return True
        except Exception as e:
            print(f"Error saving product: {str(e)}")
            return False

    def delete(self):
        """刪除產品"""
        try:
            if self.id:
                db = self.get_db()
                # 刪除相關圖片
                images = ProductImage.filter_by(product_id=self.id)
                for image in images:
                    image.delete()

                db.collection(self.COLLECTION).document(str(self.id)).delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting product: {str(e)}")
            return False

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'sub_category_id': self.sub_category_id,
            'name': self.name,
            'model': self.model,
            'price': str(self.price) if self.price else None,
            'description': self.description,
            'specifications': self.specifications,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }


class ProductImage:
    """產品圖片模型 - 使用 Firebase Storage"""
    COLLECTION = 'product_images'

    def __init__(self, product_id=None, image_url=None, image_type=None,
                 is_main=False, image_id=None):
        self.id = image_id
        self.product_id = product_id
        self.image_url = image_url  # 改用 URL 而非 BLOB
        self.image_type = image_type
        self.is_main = is_main
        self.created_at = datetime.utcnow()

    @staticmethod
    def get_db():
        return current_app.db

    @classmethod
    def get(cls, image_id):
        """根據ID獲取圖片"""
        if not image_id:
            return None
        db = cls.get_db()
        doc = db.collection(cls.COLLECTION).document(str(image_id)).get()
        if doc.exists:
            return cls._from_doc(doc)
        return None

    @classmethod
    def filter_by(cls, **kwargs):
        """根據條件查詢圖片"""
        db = cls.get_db()
        query = db.collection(cls.COLLECTION)

        for key, value in kwargs.items():
            if key == 'product_id':
                query = query.where(key, '==', str(value))
            else:
                query = query.where(key, '==', value)

        docs = query.stream()
        return [cls._from_doc(doc) for doc in docs]

    @classmethod
    def _from_doc(cls, doc):
        """從 Firestore 文檔創建對象"""
        data = doc.to_dict()
        obj = cls.__new__(cls)
        obj.id = doc.id
        obj.product_id = data.get('product_id')
        obj.image_url = data.get('image_url')
        obj.image_type = data.get('image_type')
        obj.is_main = data.get('is_main', False)
        obj.created_at = data.get('created_at')
        return obj

    def save(self):
        """儲存圖片信息"""
        try:
            db = self.get_db()
            data = {
                'product_id': str(self.product_id),
                'image_url': self.image_url,
                'image_type': self.image_type,
                'is_main': self.is_main
            }

            if self.id:
                db.collection(self.COLLECTION).document(str(self.id)).update(data)
            else:
                data['created_at'] = self.created_at
                _, doc_ref = db.collection(self.COLLECTION).add(data)
                self.id = doc_ref.id

            return True
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            return False

    def delete(self):
        """刪除圖片"""
        try:
            if self.id:
                db = self.get_db()
                # 從 Storage 刪除實際檔案
                if self.image_url:
                    self.delete_from_storage()

                db.collection(self.COLLECTION).document(str(self.id)).delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting image: {str(e)}")
            return False

    def upload_to_storage(self, image_data, content_type):
        """上傳圖片到 Firebase Storage"""
        try:
            bucket = storage.bucket()
            filename = f'products/{self.product_id}/{uuid.uuid4()}.jpg'
            blob = bucket.blob(filename)
            blob.upload_from_string(image_data, content_type=content_type)
            blob.make_public()

            self.image_url = blob.public_url
            self.image_type = content_type
            return True
        except Exception as e:
            print(f"Error uploading image: {str(e)}")
            return False

    def delete_from_storage(self):
        """從 Firebase Storage 刪除圖片"""
        try:
            if self.image_url:
                bucket = storage.bucket()
                # 從 URL 提取檔案路徑
                path = self.image_url.split(bucket.name + '/')[-1].split('?')[0]
                blob = bucket.blob(path)
                blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting from storage: {str(e)}")
            return False

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'image_url': self.image_url,
            'image_type': self.image_type,
            'is_main': self.is_main,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }