from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# 載入環境變數
load_dotenv()

# 初始化 JWT
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # 環境設定
    config_name = os.getenv("FLASK_CONFIG", "development")
    from config import config as app_config
    app.config.from_object(app_config[config_name])

    # 初始化 Firebase
    from config import Config
    app.db = Config.init_firebase()

    # 初始化 JWT
    jwt.init_app(app)
    CORS(app)

    app.config['JWT_IDENTITY_CLAIM'] = 'sub'

    # 註冊藍圖
    from api import register_blueprints
    register_blueprints(app)

    return app

if __name__ == '__main__':
    app = create_app()
    host = app.config.get("HOST", "127.0.0.1")
    port = app.config.get("PORT", 5000)
    debug = app.config["DEBUG"]

    print("Firebase initialized successfully!")
    app.run(host=host, port=port, debug=debug)