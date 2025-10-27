from flask import Blueprint, request, jsonify

route_bp = Blueprint("routes", __name__)

@route_bp.route("/plan", methods=["GET", "POST"])
def plan_route():
    """简易路线规划：支持 GET(查询参数) 与 POST(JSON/表单)"""
    if request.method == "GET":
        start = request.args.get("start")
        end = request.args.get("end")
        wp = request.args.getlist("waypoints")
        if len(wp) == 1 and wp[0] and "," in wp[0]:
            waypoints = [w for w in wp[0].split(",") if w]
        else:
            waypoints = wp
    else:
        data = request.get_json(silent=True) or {}
        start = data.get("start") or request.form.get("start")
        end = data.get("end") or request.form.get("end")
        if isinstance(data.get("waypoints"), list):
            waypoints = data["waypoints"]
        else:
            wp_multi = request.form.getlist("waypoints")
            if wp_multi:
                waypoints = wp_multi
            else:
                s = request.form.get("waypoints", "")
                waypoints = [w for w in s.split(",") if w] if s else []

    if not start or not end:
        return jsonify({"status": "error", "message": "start 和 end 必填"}), 400

    route = [start] + waypoints + [end]
    total_distance = len(route) * 2.5
    return jsonify({
        "status": "success",
        "message": "路线规划成功",
        "route": route,
        "distance_km": total_distance
    })