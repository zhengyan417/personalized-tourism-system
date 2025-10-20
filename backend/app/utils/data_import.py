import csv
import os
print("当前运行文件：", os.path.abspath(__file__))
print("文件是否定义 DB_CONFIG：", 'DB_CONFIG' in globals())
print("Python 当前工作目录：", os.getcwd())

import pymysql

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lyy060519',
    'database': 'travel_system',
    'charset': 'utf8mb4'
}

def import_attractions(csv_path):
    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    with open(csv_path, 'r', encoding='utf-8') as file:
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
    print(f"✅ 成功导入 {count} 条景点数据！")

if __name__ == "__main__":
    csv_path = "../../docs/database/attractions_data.csv"
    import_attractions(csv_path)
