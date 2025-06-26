from dotenv import load_dotenv
load_dotenv()

import os
import MySQLdb
import MySQLdb.cursors

REQUIRED_ENV_VARS = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
def check_env():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"缺少数据库环境变量: {', '.join(missing)}，请在.env文件中设置")

def get_connection():
    check_env()
    return MySQLdb.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        passwd=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        charset="utf8mb4"
    )

def get_schema():
    conn = get_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]
        schema = {}
        for table in tables:
            cursor.execute(f"DESCRIBE `{table}`")
            columns = cursor.fetchall()
            schema[table] = columns
        return schema
    finally:
        cursor.close()
        conn.close()

def run_sql(sql: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        return {"success": True, "results": results, "rowCount": len(results)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close() 