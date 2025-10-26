from flask import Blueprint, request, jsonify

route_bp = Blueprint("routes", __name__)

@route_bp.route("/plan", methods=["POST"])
def plan_route():
    """简易路线规划示例"""
    data = request.get_json()
    start = data.get("start")
    end = data.get("end")
    waypoints = data.get("waypoints", [])

    # 模拟路径规划结果
    route = [start] + waypoints + [end]
    total_distance = len(route) * 2.5  # 模拟距离（单位：km）

    return jsonify({
        "status": "success",
        "message": "路线规划成功",
        "route": route,
        "distance_km": total_distance
    })
