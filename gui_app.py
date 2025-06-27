import streamlit as st
import requests
from tongyi_api_nl2sql import nl2sql
import pandas as pd

MCP_URL = "http://localhost:8000"

st.set_page_config(page_title="NL2SQL 查询工具", page_icon="🧠", layout="wide")

# 顶部 Banner 样式
st.markdown("""
    <div style='background: linear-gradient(to right, #667eea, #764ba2); padding: 1em; border-radius: 10px;'>
        <h1 style='color: white;'>🧠 自然语言转SQL查询工具</h1>
        <p style='color: #f0f0f0;'>支持自然语言转SQL、结构化表浏览、智能数据查询，请确保MCP服务运行中。</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.image("https://img.icons8.com/color/96/000000/database.png", width=64)
st.sidebar.title("功能菜单")
choice = st.sidebar.radio("请选择功能：", ["💬 自然语言查询", "📂 显示所有表结构", "🔍 查询单表结构"])
st.sidebar.markdown("---")
st.sidebar.info(" 作者：唐镱航 | Powered by Streamlit")

def divider():
    st.markdown("<hr style='border:1px solid #e0e0e0; margin:1.5em 0;'>", unsafe_allow_html=True)

def get_schema(table=None):
    params = {"table": table} if table else {}
    try:
        resp = requests.get(f"{MCP_URL}/schema", params=params, timeout=5)
        return resp.json().get("schema", {})
    except Exception as e:
        st.error(f"获取schema失败：{e}")
        return {}

def run_sql(sql):
    try:
        resp = requests.post(f"{MCP_URL}/query", json={"sql": sql}, timeout=10)
        return resp.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def show_all_tables_and_schema():
    schema = get_schema()
    if not schema:
        st.warning("未获取到任何表结构，请检查MCP服务。")
    for table, columns in schema.items():
        with st.container():
            st.markdown(f"#### 📋 表名：`{table}`")
            st.dataframe(pd.DataFrame(columns), use_container_width=True, height=220)
            divider()

def show_table_schema_by_name():
    table_name = st.text_input("请输入表名（精确匹配）", help="如：student、course")
    if table_name:
        schema = get_schema(table_name)
        if table_name in schema:
            st.markdown(f"#### 📋 表名：`{table_name}`")
            st.dataframe(pd.DataFrame(schema[table_name]), use_container_width=True, height=220)
        else:
            st.warning("表不存在或无结构信息")
        divider()

def nl_query_loop(schema):
    st.markdown("### 💬 自然语言查询")
    nl_query = st.text_area("请输入查询问题", height=80)
    if st.button("执行查询", use_container_width=True):
        if not nl_query.strip():
            st.warning("请输入查询内容")
            return
        with st.spinner("⏳ 正在生成SQL并查询..."):
            sql = nl2sql(nl_query, schema)
            st.code(sql, language="sql")
            result = run_sql(sql)
            if result.get("success"):
                st.success("✅ 查询成功")
                if result.get("results"):
                    st.dataframe(pd.DataFrame(result["results"]), use_container_width=True, height=350)
                else:
                    st.info("查询成功，但无数据返回")
            else:
                st.error(f"查询失败：{result.get('error', '未知错误')}")
        divider()

def main():
    schema = get_schema()
    if choice.startswith("💬"):
        nl_query_loop(schema)
    elif choice.startswith("📂"):
        show_all_tables_and_schema()
    elif choice.startswith("🔍"):
        show_table_schema_by_name()

if __name__ == "__main__":
    main()
