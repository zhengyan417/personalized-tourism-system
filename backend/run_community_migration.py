import pymysql
import os

# 数据库配置
config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'lyy060519',
    'database': 'travel_system',
    'charset': 'utf8mb4'
}

# 读取SQL文件
sql_file = 'migrations/create_community_tables.sql'
with open(sql_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 连接数据库
connection = pymysql.connect(**config)

try:
    with connection.cursor() as cursor:
        # 分割SQL语句（按分号和DELIMITER分割）
        statements = []
        current_stmt = []
        delimiter = ';'
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # 处理DELIMITER命令
            if line.upper().startswith('DELIMITER'):
                parts = line.split()
                if len(parts) > 1:
                    delimiter = parts[1]
                continue
            
            # 跳过注释和空行
            if not line or line.startswith('--'):
                continue
            
            current_stmt.append(line)
            
            # 检查是否是语句结束
            if line.endswith(delimiter):
                stmt = ' '.join(current_stmt)
                if delimiter != ';':
                    stmt = stmt.replace(delimiter, '')
                else:
                    stmt = stmt.rstrip(';')
                
                if stmt.strip():
                    statements.append(stmt)
                current_stmt = []
        
        # 执行所有语句
        for i, stmt in enumerate(statements, 1):
            try:
                if stmt.strip():
                    cursor.execute(stmt)
                    print(f"✓ 执行语句 {i}/{len(statements)}")
            except Exception as e:
                # 对于ALTER TABLE IF NOT EXISTS等语句，忽略已存在的错误
                if 'Duplicate column name' in str(e) or 'already exists' in str(e):
                    print(f"⚠ 语句 {i} 已存在，跳过: {str(e)[:100]}")
                else:
                    print(f"✗ 语句 {i} 错误: {e}")
                    print(f"SQL: {stmt[:200]}...")
        
        connection.commit()
        print("\n✅ 社区功能数据库迁移完成！")
        
except Exception as e:
    connection.rollback()
    print(f"❌ 迁移失败: {e}")
finally:
    connection.close()
