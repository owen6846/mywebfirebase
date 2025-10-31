from datetime import datetime
from flask import current_app

class MainCategory:
    """產品大分類模型"""
    COLLECTION = 'main_categories'

    def __init__(self, name=None, description=None, category_id=None):
        self.id = category_id
        self.name = name
        self.description = description
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def get_db():
        return current_app.db

    @classmethod
    def get(cls, category_id):
        """根據ID獲取主分類"""
        if not category_id:
            return None
        db = cls.get_db()
        doc = db.collection(cls.COLLECTION).document(str(category_id)).get()
        if doc.exists:
            return cls._from_doc(doc)
        return None

    @classmethod
    def all(cls):
        """獲取所有主分類"""
        db = cls.get_db()
        docs = db.collection(cls.COLLECTION).stream()
        return [cls._from_doc(doc) for doc in docs]

    @classmethod
    def _from_doc(cls, doc):
        """從 Firestore 文檔創建對象"""
        data = doc.to_dict()
        obj = cls.__new__(cls)
        obj.id = doc.id
        obj.name = data.get('name')
        obj.description = data.get('description')
        obj.created_at = data.get('created_at')
        obj.updated_at = data.get('updated_at')
        return obj

    def save(self):
        """儲存主分類"""
        try:
            db = self.get_db()
            data = {
                'name': self.name,
                'description': self.description,
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
            print(f"Error saving category: {str(e)}")
            return False

    def delete(self):
        """刪除主分類"""
        try:
            if self.id:
                db = self.get_db()
                # 先刪除所有子分類
                subcategories = SubCategory.filter_by(main_category_id=self.id)
                for subcat in subcategories:
                    subcat.delete()

                db.collection(self.COLLECTION).document(str(self.id)).delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting category: {str(e)}")
            return False

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }


class SubCategory:
    """產品子分類模型"""
    COLLECTION = 'sub_categories'

    def __init__(self, main_category_id=None, name=None, description=None, category_id=None):
        self.id = category_id
        self.main_category_id = main_category_id
        self.name = name
        self.description = description
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def get_db():
        return current_app.db

    @classmethod
    def get(cls, category_id):
        """根據ID獲取子分類"""
        if not category_id:
            return None
        db = cls.get_db()
        doc = db.collection(cls.COLLECTION).document(str(category_id)).get()
        if doc.exists:
            return cls._from_doc(doc)
        return None

    @classmethod
    def filter_by(cls, **kwargs):
        """根據條件查詢子分類 - 返回列表"""
        db = cls.get_db()
        query = db.collection(cls.COLLECTION)

        for key, value in kwargs.items():
            query = query.where(key, '==', str(value))

        docs = query.stream()
        return [cls._from_doc(doc) for doc in docs]

    @classmethod
    def all(cls):
        """獲取所有子分類"""
        db = cls.get_db()
        docs = db.collection(cls.COLLECTION).stream()
        return [cls._from_doc(doc) for doc in docs]

    @classmethod
    def _from_doc(cls, doc):
        """從 Firestore 文檔創建對象"""
        data = doc.to_dict()
        obj = cls.__new__(cls)
        obj.id = doc.id
        obj.main_category_id = data.get('main_category_id')
        obj.name = data.get('name')
        obj.description = data.get('description')
        obj.created_at = data.get('created_at')
        obj.updated_at = data.get('updated_at')
        return obj

    def save(self):
        """儲存子分類"""
        try:
            db = self.get_db()
            data = {
                'main_category_id': str(self.main_category_id),
                'name': self.name,
                'description': self.description,
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
            print(f"Error saving subcategory: {str(e)}")
            return False

    def delete(self):
        """刪除子分類"""
        try:
            if self.id:
                db = self.get_db()
                # 刪除相關產品
                from .product import Product
                products = Product.filter_by(sub_category_id=self.id)
                for product in products:
                    product.delete()

                db.collection(self.COLLECTION).document(str(self.id)).delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting subcategory: {str(e)}")
            return False

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'main_category_id': self.main_category_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }