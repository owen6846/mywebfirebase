import os
from datetime import timedelta
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage as firebase_storage

# 載入環境變數
env = os.getenv('FLASK_ENV', 'development')
load_dotenv(f'.env.{env}')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Firebase 配置
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')

    # 上傳檔案相關設定
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    PORT = int(os.getenv("FLASK_PORT", 5000))

    @staticmethod
    def init_firebase():
        """初始化 Firebase"""
        cred_path = Config.FIREBASE_CREDENTIALS_PATH
        storage_bucket = Config.FIREBASE_STORAGE_BUCKET

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': storage_bucket
            })

        return firestore.client()

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}