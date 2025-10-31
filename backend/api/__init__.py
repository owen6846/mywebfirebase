from flask import Blueprint

def register_blueprints(app):
    """註冊所有前台API藍圖到Flask應用"""
    from .auth import auth_bp
    from .categories import categories_bp
    from .products import products_bp
    from .documents import documents_bp
    from .carousel import carousel_bp

    # 前台API註冊
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(carousel_bp, url_prefix='/api/carousel')