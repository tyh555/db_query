from flask import Flask, request, jsonify
import os
import MySQLdb
import MySQLdb.cursors
from dotenv import load_dotenv
import datetime
import threading
import re

load_dotenv()

app = Flask(__name__)

LOG_FILE = "logs/query.log"
LOG_DIR = "logs"
log_lock = threading.Lock()

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

SENSITIVE_FIELDS = {"password", "salary"}

INJECTION_PATTERNS = [
    r"(--|#|/\*.*?\*/)",  # 注释符号
    r";\s*(select|update|delete|insert|\bdrop\b|\bcreate\b)",  # 多语句执行符
    r"\b(OR|AND)\b\s+[^=]*=",  # OR/AND 语句绕过
    r"\b(UNION|SLEEP|BENCHMARK|LOAD_FILE|INTO OUTFILE)\b",  # 高危操作
    r"\b1\s*=\s*1\b", r"\b0\s*=\s*0\b",  # 恒等逻辑
    r"['\"]\s*\+\s*['\"]",  # 字符串拼接（如 'a' + 'b'）
]

def get_connection():
    return MySQLdb.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        passwd=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        charset="utf8mb4"
    )

def log_query(sql):
    with log_lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}]\n{sql}\n\n")

def is_safe_select(sql):
    # 只允许以SELECT开头，忽略前导空白和大小写
    sql_strip = sql.strip().lower()
    return sql_strip.startswith('select')

def contains_sensitive_field(sql):
    # 提取所有字段名（简单正则，适用于SELECT ... FROM ... 语句）
    sql_lower = sql.lower()
    # 只检查select部分
    m = re.match(r"\s*select\s+(.*?)\s+from\s", sql_lower, re.DOTALL)
    if not m:
        return False
    select_part = m.group(1)
    # 拆分字段
    fields = [f.strip().strip('`"') for f in select_part.split(',')]
    for field in fields:
        # 只要字段名包含敏感词就拒绝
        for sensitive in SENSITIVE_FIELDS:
            if sensitive in field:
                return True
    return False

def is_sql_injection(sql):
    sql_lower = sql.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, sql_lower, re.DOTALL):
            return True
    return False

@app.route('/schema', methods=['GET'])
def schema():
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
        return jsonify({"success": True, "schema": schema})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    sql = data.get("sql")
    if not sql:
        return jsonify({"success": False, "error": "Missing SQL statement."}), 400
    if not is_safe_select(sql):
        return jsonify({"success": False, "error": "只允许SELECT语句，禁止非只读操作。"}), 403
    if contains_sensitive_field(sql):
        return jsonify({"success": False, "error": "禁止查询敏感字段（如 password、salary 等）。"}), 403
    if is_sql_injection(sql):
        return jsonify({"success": False, "error": "检测到疑似SQL注入攻击，已拦截。"}), 403
    log_query(sql)
    conn = get_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        return jsonify({"success": True, "results": results, "rowCount": len(results)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return content, 200, {"Content-Type": "text/plain; charset=utf-8"}
    except FileNotFoundError:
        return "No logs found.", 200, {"Content-Type": "text/plain; charset=utf-8"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
