# 文件路径：backend/app/routes/place_query.py
# 模块功能：景点查询接口（邻近搜索、类别过滤）
# 模块负责人：C 同学

from flask import Blueprint, request, jsonify
from app.utils.database import get_db
import math

# 创建蓝图对象
place_bp = Blueprint('place', __name__)

# 计算两点之间的距离（Haversine公式）
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 地球半径（千米）
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# -----------------------------------------
# GET /api/places/nearby
# 邻近查询 + 类别过滤
# -----------------------------------------
@place_bp.route('/nearby', methods=['GET'])
def get_nearby_places():
    """
    示例请求：
        GET /api/places/nearby?lat=39.9&lon=116.4&radius=5&category=景点
    """
    try:
        lat = float(request.args.get('lat', 0))
        lon = float(request.args.get('lon', 0))
        radius = float(request.args.get('radius', 10))  # 默认10km
        category = request.args.get('category', None)

        db = get_db()
        with db.cursor() as cursor:
            if category:
                sql = "SELECT * FROM attractions WHERE category=%s"
                cursor.execute(sql, (category,))
            else:
                sql = "SELECT * FROM attractions"
                cursor.execute(sql)
            results = cursor.fetchall()

        # 根据坐标过滤范围
        nearby = []
        for r in results:
            if r['latitude'] is not None and r['longitude'] is not None:
                distance = haversine(lat, lon, r['latitude'], r['longitude'])
                if distance <= radius:
                    r['distance_km'] = round(distance, 2)
                    nearby.append(r)

        nearby.sort(key=lambda x: x['distance_km'])
        return jsonify({
            "status": "success",
            "count": len(nearby),
            "data": nearby
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
