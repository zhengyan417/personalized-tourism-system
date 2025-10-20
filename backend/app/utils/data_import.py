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

def import_attractions(csv_path):
    csv_path = Path(csv_path).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    with csv_path.open('r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            sql = """
                INSERT INTO attractions (name, category, latitude, longitude, description)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                row['name'],
                row['category'],
                float(row['latitude']),
                float(row['longitude']),
                row['description']
            ))
            count += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ 成功导入 {count} 条景点数据！来源：{csv_path}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]

    attractions_csv = project_root / "docs" / "database" / "attractions_data.csv"
    facilities_csv = project_root / "docs" / "database" / "facilities_data.csv"

    import_attractions(attractions_csv)
    import_attractions(facilities_csv)  # 复用同一函数导入设施数据

