import os
from query_controller_db_query import get_schema, run_sql
from tongyi_api_nl2sql import nl2sql

from tabulate import tabulate
from colorama import init, Fore, Style

init(autoreset=True)


def main():
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + "欢迎使用自然语言转 SQL 查询工具！（输入 exit 或 quit 退出）")
    print(Fore.CYAN + "=" * 60)

    schema = get_schema()
    while True:
        nl_query = input(Fore.YELLOW + "\n请输入您的查询问题: " + Style.RESET_ALL)
        if nl_query.strip().lower() in ("exit", "quit"):
            print(Fore.CYAN + "\n感谢使用，再见！")
            break
        try:
            sql = nl2sql(nl_query, schema)
            print(Fore.BLUE + "\n生成的 SQL 语句：" + Fore.RESET)
            print(Fore.LIGHTWHITE_EX + f"{sql}")

            result = run_sql(sql)
            if result["success"]:
                print(Fore.GREEN + "\n查询成功，结果如下：")
                if result["results"]:
                    headers = result["results"][0].keys()
                    rows = [row.values() for row in result["results"]]
                    print(tabulate(rows, headers=headers, tablefmt="grid"))
                else:
                    print(Fore.YELLOW + "查询成功，但结果为空。")
            else:
                print(Fore.RED + f"\n查询失败：{result['error']}")
        except Exception as e:
            print(Fore.RED + f"\n发生错误：{e}")


if __name__ == "__main__":
    main()
