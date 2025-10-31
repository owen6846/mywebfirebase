from datetime import datetime
from flask import current_app
from firebase_admin import storage
import uuid

class Carousel:
    """輪播圖模型 - 使用 Firebase Storage"""
    COLLECTION = 'carousels'

    def __init__(self, title=None, description=None, image_url=None,
                 image_type=None, link_url=None, order_num=0,
                 is_active=True, carousel_id=None):
        self.id = carousel_id
        self.title = title
        self.description = description
        self.image_url = image_url  # 改用 URL
        self.image_type = image_type
        self.link_url = link_url
        self.order_num = order_num
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def get_db():
        return current_app.db

    @classmethod
    def get(cls, carousel_id):
        """根據ID獲取輪播圖"""
        if not carousel_id:
            return None
        db = cls.get_db()
        doc = db.collection(cls.COLLECTION).document(str(carousel_id)).get()
        if doc.exists:
            return cls._from_doc(doc)
        return None

    @classmethod
    def filter_by(cls, **kwargs):
        """根據條件查詢輪播圖"""
        db = cls.get_db()
        query = db.collection(cls.COLLECTION)

        for key, value in kwargs.items():
            query = query.where(key, '==', value)

        docs = query.stream()
        return [cls._from_doc(doc) for doc in docs]

    @classmethod
    def order_by(cls, field):
        """根據欄位排序"""
        db = cls.get_db()
        docs = db.collection(cls.COLLECTION).order_by(field).stream()
        return [cls._from_doc(doc) for doc in docs]

    @classmethod
    def all(cls):
        """獲取所有輪播圖"""
        db = cls.get_db()
        docs = db.collection(cls.COLLECTION).stream()
        return [cls._from_doc(doc) for doc in docs]

    @classmethod
    def _from_doc(cls, doc):
        """從 Firestore 文檔創建對象"""
        data = doc.to_dict()
        obj = cls.__new__(cls)
        obj.id = doc.id
        obj.title = data.get('title')
        obj.description = data.get('description')
        obj.image_url = data.get('image_url')
        obj.image_type = data.get('image_type')
        obj.link_url = data.get('link_url')
        obj.order_num = data.get('order_num', 0)
        obj.is_active = data.get('is_active', True)
        obj.created_at = data.get('created_at')
        obj.updated_at = data.get('updated_at')
        return obj

    def save(self):
        """儲存輪播圖"""
        try:
            db = self.get_db()
            data = {
                'title': self.title,
                'description': self.description,
                'image_url': self.image_url,
                'image_type': self.image_type,
                'link_url': self.link_url,
                'order_num': self.order_num,
                'is_active': self.is_active,
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
            print(f"Error saving carousel: {str(e)}")
            return False

    def delete(self):
        """刪除輪播圖"""
        try:
            if self.id:
                db = self.get_db()
                # 從 Storage 刪除實際圖片
                if self.image_url:
                    self.delete_from_storage()

                db.collection(self.COLLECTION).document(str(self.id)).delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting carousel: {str(e)}")
            return False

    def upload_to_storage(self, image_data, content_type):
        """上傳圖片到 Firebase Storage"""
        try:
            bucket = storage.bucket()
            filename = f'carousels/{uuid.uuid4()}.jpg'
            blob = bucket.blob(filename)
            blob.upload_from_string(image_data, content_type=content_type)
            blob.make_public()

            self.image_url = blob.public_url
            self.image_type = content_type
            return True
        except Exception as e:
            print(f"Error uploading carousel image: {str(e)}")
            return False

    def delete_from_storage(self):
        """從 Firebase Storage 刪除圖片"""
        try:
            if self.image_url:
                bucket = storage.bucket()
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
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'link_url': self.link_url,
            'order_num': self.order_num,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }