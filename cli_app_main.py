import requests
from tongyi_api_nl2sql import nl2sql

from tabulate import tabulate
from colorama import init, Fore, Style
import sys

# 初始化颜色输出
init(autoreset=True)

MCP_URL = "http://localhost:8000"

PAGE_SIZE = 10

MENU_BANNER = f"""
{Fore.CYAN}{'='*60}
{Fore.GREEN} 欢迎使用自然语言转 SQL 查询工具！
{Fore.CYAN}{'='*60}
"""

MENU_OPTIONS = f"""
{Fore.LIGHTWHITE_EX}请选择功能：
  {Fore.YELLOW}1{Fore.LIGHTWHITE_EX}. 输入自然语言查询
  {Fore.YELLOW}2{Fore.LIGHTWHITE_EX}. 显示所有表名及其模式
  {Fore.YELLOW}3{Fore.LIGHTWHITE_EX}. 按表名查看表结构
  {Fore.YELLOW}quit{Fore.LIGHTWHITE_EX}. 退出程序
"""

MENU_LINE = f"{Fore.CYAN}{'-'*60}"

def print_paginated_results(results):
    total = len(results)
    if total == 0:
        print(Fore.YELLOW + "查询成功，但结果为空。")
        return True  # 正常返回主循环
    page = 0
    while True:
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_results = results[start:end]
        headers = page_results[0].keys() if page_results else []
        rows = [row.values() for row in page_results]
        print(Fore.GREEN + f"\n第 {page+1} 页 / 共 {((total-1)//PAGE_SIZE)+1} 页：")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        if end >= total:
            print(Fore.CYAN + "\n已显示全部结果。")
            return True  # 正常返回主循环
        user_input = input(Fore.YELLOW + "输入 next 查看下一页，exit 继续下一次查询，quit 退出程序: " + Style.RESET_ALL).strip().lower()
        if user_input == "quit":
            print(Fore.CYAN + "\n感谢使用，再见！")
            exit(0)
        elif user_input == "exit":
            print(Fore.CYAN + "\n已切换下一次查询。")
            return True  # 返回主循环
        elif user_input == "next":
            page += 1
        else:
            print(Fore.YELLOW + "输入无效，已退出分页显示，返回主菜单。")
            return True

def show_all_tables_and_schema():
    print(Fore.LIGHTWHITE_EX + "正在获取所有表名及其模式...")
    try:
        resp = requests.get(f"{MCP_URL}/schema")
        data = resp.json()
        if not resp.ok or not data.get("success"):
            print(Fore.RED + f"获取失败: {resp.text}")
            return
        schema = data["schema"]
        for table, columns in schema.items():
            print(Fore.CYAN + f"\n表名: {table}")
            if columns:
                print(tabulate(columns, headers="keys", tablefmt="grid"))
            else:
                print(Fore.YELLOW + "(无字段)")
    except Exception as e:
        print(Fore.RED + f"获取表结构失败: {e}")

def show_table_schema_by_name():
    table_name = input(Fore.YELLOW + "请输入要查询的表名: " + Style.RESET_ALL).strip()
    if not table_name:
        print(Fore.YELLOW + "表名不能为空，已返回主菜单。")
        return
    try:
        resp = requests.get(f"{MCP_URL}/schema", params={"table": table_name})
        data = resp.json()
        if resp.status_code == 404 or not data.get("success"):
            print(Fore.RED + f"表 {table_name} 不存在或获取失败: {data.get('error', resp.text)}")
            return
        schema = data["schema"][table_name]
        print(Fore.CYAN + f"\n表名: {table_name}")
        if schema:
            print(tabulate(schema, headers="keys", tablefmt="grid"))
        else:
            print(Fore.YELLOW + "(无字段)")
    except Exception as e:
        print(Fore.RED + f"获取表结构失败: {e}")

def nl_query_loop(schema):
    while True:
        nl_query = input(Fore.YELLOW + "\n请输入您的查询问题(exit 返回主菜单，quit 退出程序): " + Style.RESET_ALL)
        if nl_query.strip().lower() == "quit":
            print(Fore.CYAN + "\n感谢使用，再见！")
            exit(0)
        if nl_query.strip().lower() == "exit":
            print(Fore.CYAN + "\n已返回主菜单。")
            break
        try:
            sql = nl2sql(nl_query, schema)
            print(Fore.BLUE + "\n生成的 SQL 语句：")
            print(Fore.LIGHTWHITE_EX + sql)
            response = requests.post(f"{MCP_URL}/query", json={"sql": sql})
            result = response.json()
            if result.get("success"):
                print(Fore.GREEN + "\n查询成功，结果如下：")
                print_paginated_results(result["results"])
            else:
                print(Fore.RED + f"查询失败：{result.get('error', '未知错误')}")
        except Exception as e:
            print(Fore.RED + f"发生错误：{e}")

def main():
    print(MENU_BANNER)
    # 获取 schema
    print(Fore.LIGHTWHITE_EX + "正在连接 MCP 服务并获取数据库结构...")
    try:
        resp = requests.get(f"{MCP_URL}/schema")
        if not resp.ok or not resp.json().get("success"):
            print(Fore.RED + f"无法获取数据库结构: {resp.text}")
            return
        schema = resp.json()["schema"]
        print(Fore.GREEN + "数据库结构获取成功！")
    except Exception as e:
        print(Fore.RED + f"MCP 服务连接失败: {e}")
        return
    while True:
        print(MENU_LINE)
        print(MENU_OPTIONS)
        print(MENU_LINE)
        choice = input(Fore.YELLOW + "请输入选项编号: " + Style.RESET_ALL).strip().lower()
        if choice == "1":
            nl_query_loop(schema)
        elif choice == "2":
            show_all_tables_and_schema()
        elif choice == "3":
            show_table_schema_by_name()
        elif choice == "quit":
            print(Fore.CYAN + "\n感谢使用，再见！")
            break
        else:
            print(Fore.YELLOW + "无效选项，请重新输入。")

if __name__ == "__main__":
    main()
