# /backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from app.utils.database import init_db
from app.routes.place_query import place_bp
from app.routes.travel_diary import diary_bp
from app.routes.recommendation import rec_bp
from app.routes.route_planning import route_bp

def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # 允许跨域请求
    CORS(app)

    # 初始化数据库连接
    init_db(app)

    # 注册路由蓝图
    app.register_blueprint(place_bp, url_prefix='/api/places')
    app.register_blueprint(diary_bp, url_prefix='/api/diaries')
    app.register_blueprint(rec_bp, url_prefix="/api/recommendations")
    app.register_blueprint(route_bp, url_prefix="/api/routes")

    return app
