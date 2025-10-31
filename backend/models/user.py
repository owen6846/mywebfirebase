from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import current_app

class User:
    """用戶模型"""
    COLLECTION = 'users'

    def __init__(self, username=None, password=None, email=None, is_admin=False, user_id=None):
        self.id = user_id
        self.username = username
        self.password_hash = generate_password_hash(password) if password else None
        self.email = email
        self.is_admin = is_admin
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def get_db():
        return current_app.db

    @classmethod
    def get(cls, user_id):
        """根據ID獲取用戶"""
        if not user_id:
            return None
        db = cls.get_db()
        doc = db.collection(cls.COLLECTION).document(str(user_id)).get()
        if doc.exists:
            return cls._from_doc(doc)
        return None

    @classmethod
    def filter_by(cls, **kwargs):
        """根據條件查詢用戶 - 返回單個用戶"""
        db = cls.get_db()
        query = db.collection(cls.COLLECTION)

        for key, value in kwargs.items():
            query = query.where(key, '==', value)

        docs = query.limit(1).stream()
        for doc in docs:
            return cls._from_doc(doc)
        return None

    @classmethod
    def _from_doc(cls, doc):
        """從 Firestore 文檔創建用戶對象"""
        data = doc.to_dict()
        user = cls.__new__(cls)
        user.id = doc.id
        user.username = data.get('username')
        user.password_hash = data.get('password_hash')
        user.email = data.get('email')
        user.is_admin = data.get('is_admin', False)
        user.created_at = data.get('created_at')
        user.updated_at = data.get('updated_at')
        return user

    def save(self):
        """儲存用戶"""
        try:
            db = self.get_db()
            data = {
                'username': self.username,
                'password_hash': self.password_hash,
                'email': self.email,
                'is_admin': self.is_admin,
                'updated_at': datetime.utcnow()
            }

            if self.id:
                # 更新現有用戶
                db.collection(self.COLLECTION).document(str(self.id)).update(data)
            else:
                # 創建新用戶
                data['created_at'] = self.created_at
                _, doc_ref = db.collection(self.COLLECTION).add(data)
                self.id = doc_ref.id

            return True
        except Exception as e:
            print(f"Error saving user: {str(e)}")
            return False

    def delete(self):
        """刪除用戶"""
        try:
            if self.id:
                db = self.get_db()
                db.collection(self.COLLECTION).document(str(self.id)).delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            return False

    def check_password(self, password):
        """檢查密碼"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }