import csv
import pymysql
from pathlib import Path

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lyy060519',
    'database': 'travel_system',
    'charset': 'utf8mb4'
}


# ---------- Helpers: normalization / schema guard / dedup ----------
def _norm_str(x):
    return (x or "").strip()

def _norm_float(x, digits=6):
    try:
        return round(float(x), digits)
    except Exception:
        return 0.0

def _ensure_unique_index(conn, table: str, index_name: str, cols: tuple[str, str, str]):
    """Ensure unique index exists on (name, latitude, longitude). Safe for MySQL 5.7+.
    """
    name_col, lat_col, lon_col = cols
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS c
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
              AND table_name = %s
              AND index_name = %s
            """,
            (table, index_name)
        )
        exists = int(cur.fetchone()["c"]) > 0
        if not exists:
            # 尝试创建唯一索引；若已有重复将失败
            cur.execute(f"CREATE UNIQUE INDEX {index_name} ON {table}({name_col}, {lat_col}, {lon_col})")
            conn.commit()

def _dedupe_table(conn, table: str, id_col: str):
    """Delete duplicates by (name, latitude, longitude), keep MIN(id). Also relink diaries for attractions.
    """
    with conn.cursor() as cur:
        # 建临时映射：需要删除的 -> 保留的
        cur.execute("DROP TEMPORARY TABLE IF EXISTS _dup_map")
        cur.execute(
            f"""
            CREATE TEMPORARY TABLE _dup_map (
              remove_id INT PRIMARY KEY,
              keep_id INT NOT NULL
            ) ENGINE=Memory
            """
        )
        cur.execute(
            f"""
            INSERT INTO _dup_map(remove_id, keep_id)
            SELECT t.{id_col} AS remove_id, m.min_id AS keep_id
            FROM {table} t
            JOIN (
              SELECT name, latitude, longitude, MIN({id_col}) AS min_id, COUNT(*) AS c
              FROM {table}
              GROUP BY name, latitude, longitude
              HAVING COUNT(*) > 1
            ) m
              ON t.name=m.name AND t.latitude<=>m.latitude AND t.longitude<=>m.longitude
            WHERE t.{id_col} <> m.min_id
            """
        )
        cur.execute("SELECT COUNT(*) AS c FROM _dup_map")
        to_remove = int(cur.fetchone()["c"]) or 0
        if to_remove > 0:
            # 仅 attractions 需要维护 diaries 外键
            if table == "attractions":
                cur.execute(
                    """
                    UPDATE diaries d
                    JOIN _dup_map dm ON d.attraction_id = dm.remove_id
                    SET d.attraction_id = dm.keep_id
                    """
                )
            cur.execute(
                f"""
                DELETE t FROM {table} t
                JOIN _dup_map dm ON t.{id_col} = dm.remove_id
                """
            )
            conn.commit()

def _rows_from_csv(csv_path: Path):
    with csv_path.open('r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield row


def import_attractions(csv_path):
    csv_path = Path(csv_path).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1) 先做快速规范化去重（以防索引创建失败）
    try:
        _dedupe_table(conn, "attractions", "attraction_id")
    except Exception:
        pass
    # 2) 确保唯一索引存在（触发 UPSERT 生效）
    try:
        _ensure_unique_index(conn, "attractions", "ux_attractions_name_lat_lon", ("name", "latitude", "longitude"))
    except Exception:
        # 如果库里仍有重复，索引可能创建失败；此时依赖第1步清理或后续再次尝试
        pass

    count = 0
    for row in _rows_from_csv(csv_path):
        # 兼容可选列：popularity, avg_rating, rating_count, image_url
        name = _norm_str(row.get('name'))
        category = _norm_str(row.get('category'))
        latitude = _norm_float(row.get('latitude'))
        longitude = _norm_float(row.get('longitude'))
        description = row.get('description')
        popularity = int(row.get('popularity') or 0)
        avg_rating = row.get('avg_rating')
        avg_rating = float(avg_rating) if (avg_rating not in (None, '')) else None
        rating_count = int(row.get('rating_count') or 0)
        image_url = row.get('image_url')
        visitor_count = int(row.get('visitor_count') or 0)

        sql = """
            INSERT INTO attractions (
                name, category, latitude, longitude, description,
                popularity, avg_rating, rating_count, image_url, visitor_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                category=VALUES(category),
                description=VALUES(description),
                popularity=VALUES(popularity),
                avg_rating=VALUES(avg_rating),
                rating_count=VALUES(rating_count),
                image_url=VALUES(image_url),
                visitor_count=VALUES(visitor_count)
        """
        cursor.execute(sql, (
            name, category, latitude, longitude, description,
            popularity, avg_rating, rating_count, image_url, visitor_count
        ))
        count += 1

    conn.commit()
    cursor.close()
    conn.close()
    try:
        print(f"[OK] 成功导入/更新 {count} 条景点数据，来源：{csv_path}")
    except Exception:
        # 兼容 Windows GBK 控制台
        pass


def import_facilities(csv_path):
    csv_path = Path(csv_path).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1) 先做快速规范化去重
    try:
        _dedupe_table(conn, "facilities", "facility_id")
    except Exception:
        pass
    # 2) 确保唯一索引存在
    try:
        _ensure_unique_index(conn, "facilities", "ux_facilities_name_lat_lon", ("name", "latitude", "longitude"))
    except Exception:
        pass

    count = 0
    for row in _rows_from_csv(csv_path):
        name = _norm_str(row.get('name'))
        category = _norm_str(row.get('category'))
        latitude = _norm_float(row.get('latitude'))
        longitude = _norm_float(row.get('longitude'))
        description = row.get('description')
        popularity = int(row.get('popularity') or 0)
        avg_rating = row.get('avg_rating')
        avg_rating = float(avg_rating) if (avg_rating not in (None, '')) else None
        rating_count = int(row.get('rating_count') or 0)
        image_url = row.get('image_url')
        visitor_count = int(row.get('visitor_count') or 0)

        sql = """
            INSERT INTO facilities (
                name, category, latitude, longitude, description,
                popularity, avg_rating, rating_count, image_url, visitor_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                category=VALUES(category),
                description=VALUES(description),
                popularity=VALUES(popularity),
                avg_rating=VALUES(avg_rating),
                rating_count=VALUES(rating_count),
                image_url=VALUES(image_url),
                visitor_count=VALUES(visitor_count)
        """
        cursor.execute(sql, (
            name, category, latitude, longitude, description,
            popularity, avg_rating, rating_count, image_url, visitor_count
        ))
        count += 1

    conn.commit()
    cursor.close()
    conn.close()
    try:
        print(f"[OK] 成功导入/更新 {count} 条设施数据，来源：{csv_path}")
    except Exception:
        pass

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]

    attractions_csv = project_root / "docs" / "database" / "attractions_data.csv"
    facilities_csv = project_root / "docs" / "database" / "facilities_data.csv"

    import_attractions(attractions_csv)
    if facilities_csv.exists():
        import_facilities(facilities_csv)
    else:
        print("ℹ️ 未找到 facilities_data.csv，跳过设施导入。")

