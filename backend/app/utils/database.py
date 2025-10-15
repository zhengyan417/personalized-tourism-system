# /backend/app/utils/database.py
import pymysql
from flask import g

def init_db(app):
    """初始化数据库连接"""
    @app.before_request
    def before_request():
        g.db = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            port=app.config['MYSQL_PORT'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    @app.teardown_request
    def teardown_request(exception):
        db = getattr(g, 'db', None)
        if db:
            db.close()

def get_db():
    """获取数据库连接对象"""
    return getattr(g, 'db', None)
