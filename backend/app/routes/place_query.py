# 文件路径：backend/app/routes/place_query.py
# 模块功能：景点查询接口（按ID、按类别、邻近搜索）
# 模块负责人：C 同学

from flask import Blueprint, request, jsonify
from app.utils.database import get_db
from app.utils.helpers import deduplicate_records, deduplicate_by_description
import math

# 创建蓝图对象
place_bp = Blueprint('place', __name__)

# -----------------------------------------
# GET /api/places/categories
# 获取所有景点类别
# -----------------------------------------
@place_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    返回所有景点类别列表
    示例请求：GET /api/places/categories
    """
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT category 
                FROM attractions 
                WHERE category IS NOT NULL AND category != '' 
                ORDER BY category
            """)
            rows = cursor.fetchall()
            categories = [row['category'] for row in rows]
            
        return jsonify({
            'status': 'success',
            'data': categories
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取类别失败: {str(e)}'
        }), 500

# -----------------------------------------
# 工具函数：Haversine公式计算两点距离（单位：公里）
# -----------------------------------------
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
# GET /api/places/
# 查询全部景点，可选按类别或关键字过滤
# -----------------------------------------
@place_bp.route('/', methods=['GET'])
def get_places():
    """
    示例请求：
        GET /api/places/
        GET /api/places/?category=美食
        GET /api/places/?keyword=颐和园
    """
    try:
        category = request.args.get('category')
        keyword = request.args.get('keyword')

        db = get_db()
        with db.cursor() as cursor:
            sql = "SELECT * FROM attractions WHERE 1=1"
            params = []

            if category:
                sql += " AND category = %s"
                params.append(category)

            if keyword:
                sql += " AND name LIKE %s"
                params.append(f"%{keyword}%")

            cursor.execute(sql, tuple(params))
            results = cursor.fetchall()

        # 去重：优先按 attraction_id/id；若无则用 name+坐标；最后按描述再去重
       

        return jsonify({
            "status": "success",
            "count": len(results),
            "data": results
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# -----------------------------------------
# GET /api/places/<int:attraction_id>
# 按景点ID查询单个景点详情
# -----------------------------------------
@place_bp.route('/<int:attraction_id>', methods=['GET'])
def get_place_by_id(attraction_id):
    """
    示例请求：
        GET /api/places/1
    """
    try:
        db = get_db()
        with db.cursor() as cursor:
            sql = "SELECT * FROM attractions WHERE attraction_id = %s"
            cursor.execute(sql, (attraction_id,))
            result = cursor.fetchone()

        if result:
            return jsonify({
                "status": "success",
                "data": result
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"未找到 ID={attraction_id} 的景点"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# -----------------------------------------
# GET /api/places/nearby
# 邻近查询 + 可选类别过滤
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
                sql = "SELECT * FROM attractions WHERE category = %s"
                cursor.execute(sql, (category,))
            else:
                sql = "SELECT * FROM attractions"
                cursor.execute(sql)
            results = cursor.fetchall()

        nearby = []
        for r in results:
            if r['latitude'] is not None and r['longitude'] is not None:
                distance = haversine(lat, lon, r['latitude'], r['longitude'])
                if distance <= radius:
                    r['distance_km'] = round(distance, 2)
                    nearby.append(r)

        # 去重后再排序（ID/坐标 -> 描述）
        nearby = deduplicate_records(nearby, keys=("attraction_id", "id"))
        nearby = deduplicate_by_description(nearby, description_key="description", ignore_empty=True)
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


# -----------------------------------------
# GET /api/attractions/search
# 根据景点名称搜索景点（用于AI路线导入）
# -----------------------------------------
@place_bp.route('/search', methods=['GET'], endpoint='search_attractions')
def search_attractions():
    """
    根据景点名称搜索景点，支持模糊匹配
    示例请求：GET /api/attractions/search?name=故宫
    """
    try:
        name = request.args.get('name', '').strip()
        
        if not name:
            return jsonify({
                'status': 'error',
                'message': '景点名称不能为空'
            }), 400
        
        db = get_db()
        with db.cursor() as cursor:
            # 尝试精确匹配
            cursor.execute("""
                SELECT * FROM attractions 
                WHERE name = %s 
                LIMIT 1
            """, (name,))
            result = cursor.fetchone()
            
            # 如果精确匹配失败，尝试模糊匹配
            if not result:
                cursor.execute("""
                    SELECT * FROM attractions 
                    WHERE name LIKE %s 
                    ORDER BY 
                        CASE 
                            WHEN name = %s THEN 0
                            WHEN name LIKE %s THEN 1
                            ELSE 2
                        END,
                        LENGTH(name)
                    LIMIT 5
                """, (f'%{name}%', name, f'{name}%'))
                results = cursor.fetchall()
            else:
                results = [result]
        
        return jsonify({
            'status': 'success',
            'count': len(results),
            'data': results
        }), 200
        
    except Exception as e:
        print(f'[Attractions Search] Error: {e}')
        return jsonify({
            'status': 'error',
            'message': f'搜索失败: {str(e)}'
        }), 500
