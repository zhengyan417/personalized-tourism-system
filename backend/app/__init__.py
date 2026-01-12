# /backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from app.utils.database import init_db
from app.routes.place_query import place_bp
from app.routes.travel_diary import diary_bp
from app.routes.recommendation import rec_bp
from app.routes.route_planning import route_bp
from app.routes.auth import auth_bp
from app.routes.community import community_bp
from app.routes.ai import ai_bp

def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # 确保JSON正确处理UTF-8中文
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
    
    # 配置 Session（用于登录状态保持）
    app.config['SESSION_TYPE'] = 'filesystem'  # 使用文件系统存储 session
    app.config['SESSION_PERMANENT'] = True  # session 持久化
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # session 有效期 7 天
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止 XSS 攻击
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF 保护
    # 开发环境允许 HTTP，生产环境建议设为 True
    app.config['SESSION_COOKIE_SECURE'] = False

    # 允许跨域请求，携带 Cookie 以保持登录状态
    # 支持 localhost 和局域网 IP 访问
    # 使用正则表达式模式匹配允许的来源
    CORS(app, 
         supports_credentials=True,
         origins=[
             r"http://localhost:\d+",
             r"http://127\.0\.0\.1:\d+",
             r"http://192\.168\.\d+\.\d+:\d+",
             r"http://10\.\d+\.\d+\.\d+:\d+",
             r"http://172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+:\d+"
         ],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
    print(">>> 后端服务已启动，CORS 配置已更新 (支持 localhost 和局域网访问)")

    # 初始化数据库连接
    init_db(app)

    # 注册路由蓝图
    app.register_blueprint(place_bp, url_prefix='/api/places')
    app.register_blueprint(diary_bp, url_prefix='/api/diaries')
    app.register_blueprint(rec_bp, url_prefix="/api/recommendations")
    app.register_blueprint(route_bp, url_prefix="/api/routes")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(community_bp)  # 社区功能，使用完整路径
    app.register_blueprint(ai_bp)  # AI助手代理

    return app
