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
    
    # 确保JSON正确处理UTF-8中文
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

    # 允许跨域请求，携带 Cookie 以保持登录状态
    # 明确指定允许的源（不能使用 * 当 credentials=True 时）
    CORS(app, 
         supports_credentials=True,
         origins=[
             "http://localhost:8080",
             "http://127.0.0.1:8080",
             "http://localhost:8081",
             "http://127.0.0.1:8081",
             "http://localhost:3000",
             "http://127.0.0.1:3000",
             "http://localhost:8082",
             "http://127.0.0.1:8082"
         ],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
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
