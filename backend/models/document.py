from datetime import datetime
from flask import current_app
from firebase_admin import storage
import uuid
import os

class Document:
    """文檔模型 - 使用 Firebase Storage"""
    COLLECTION = 'documents'

    def __init__(self, title=None, file_url=None, file_size=None,
                 file_type=None, requires_login=False, doc_id=None):
        self.id = doc_id
        self.title = title
        self.file_url = file_url  # 改用 URL
        self.file_size = file_size
        self.file_type = file_type
        self.requires_login = requires_login
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def get_db():
        return current_app.db

    @classmethod
    def get(cls, doc_id):
        """根據ID獲取文檔"""
        if not doc_id:
            return None
        db = cls.get_db()
        doc = db.collection(cls.COLLECTION).document(str(doc_id)).get()
        if doc.exists:
            return cls._from_doc(doc)
        return None

    @classmethod
    def filter_by(cls, **kwargs):
        """根據條件查詢文檔"""
        db = cls.get_db()
        query = db.collection(cls.COLLECTION)

        for key, value in kwargs.items():
            query = query.where(key, '==', value)

        docs = query.stream()
        return [cls._from_doc(doc) for doc in docs]

    @classmethod
    def all(cls):
        """獲取所有文檔"""
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
        obj.file_url = data.get('file_url')
        obj.file_size = data.get('file_size')
        obj.file_type = data.get('file_type')
        obj.requires_login = data.get('requires_login', False)
        obj.created_at = data.get('created_at')
        obj.updated_at = data.get('updated_at')
        return obj

    def save(self):
        """儲存文檔"""
        try:
            db = self.get_db()
            data = {
                'title': self.title,
                'file_url': self.file_url,
                'file_size': self.file_size,
                'file_type': self.file_type,
                'requires_login': self.requires_login,
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
            print(f"Error saving document: {str(e)}")
            return False

    def delete(self):
        """刪除文檔"""
        try:
            if self.id:
                db = self.get_db()
                # 從 Storage 刪除實際檔案
                if self.file_url:
                    self.delete_from_storage()

                db.collection(self.COLLECTION).document(str(self.id)).delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False

    def upload_to_storage(self, file_data, filename):
        """上傳文件到 Firebase Storage"""
        try:
            bucket = storage.bucket()
            ext = os.path.splitext(filename)[1]
            storage_path = f'documents/{uuid.uuid4()}{ext}'
            blob = bucket.blob(storage_path)
            blob.upload_from_string(file_data, content_type=self.file_type)
            blob.make_public()

            self.file_url = blob.public_url
            return True
        except Exception as e:
            print(f"Error uploading document: {str(e)}")
            return False

    def delete_from_storage(self):
        """從 Firebase Storage 刪除文件"""
        try:
            if self.file_url:
                bucket = storage.bucket()
                path = self.file_url.split(bucket.name + '/')[-1].split('?')[0]
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
            'file_url': self.file_url,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'requires_login': self.requires_login,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }