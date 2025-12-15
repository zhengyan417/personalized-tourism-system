# /backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from app.utils.database import init_db
from app.routes.place_query import place_bp
from app.routes.travel_diary import diary_bp
from app.routes.recommendation import rec_bp
from app.routes.route_planning import route_bp
from app.routes.auth import auth_bp

def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # 允许跨域请求，携带 Cookie 以保持登录状态
    # 使用正则匹配所有本地开发端口
    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": [
                r"^http://localhost:\d+$",
                r"^http://127\.0\.0\.1:\d+$"
            ]
        }
    })
    
    print(">>> 后端服务已启动，CORS 配置已更新 (支持 Cookie)")

    # 初始化数据库连接
    init_db(app)

    # 注册路由蓝图
    app.register_blueprint(place_bp, url_prefix='/api/places')
    app.register_blueprint(diary_bp, url_prefix='/api/diaries')
    app.register_blueprint(rec_bp, url_prefix="/api/recommendations")
    app.register_blueprint(route_bp, url_prefix="/api/routes")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    return app
