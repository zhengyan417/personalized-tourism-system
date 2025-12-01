# /backend/config.py
import os


class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'lyy060519')
    MYSQL_DB = os.getenv('MYSQL_DB', 'travel_system')
    JSON_AS_ASCII = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')

    # 第三方导航服务
    AMAP_API_KEY = os.getenv('AMAP_API_KEY')
    AMAP_API_SECRET = os.getenv('AMAP_API_SECRET')
    OSRM_BASE_URL = os.getenv('OSRM_BASE_URL', 'https://router.project-osrm.org')
