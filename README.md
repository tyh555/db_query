# 自然语言转SQL查询系统

本项目实现了一个支持自然语言转SQL的智能数据库查询系统，支持命令行（CLI）和可视化（Streamlit GUI）两种交互方式，后端基于MCP服务统一管理数据库访问，集成通义大模型API实现自然语言到SQL的智能转换。

---

## 目录结构

```
.
├── main.py                # MCP服务，提供/schema和/query等HTTP接口
├── cli_app_main.py        # 命令行主菜单交互入口
├── gui_app.py             # Streamlit可视化界面入口
├── tongyi_api_nl2sql.py   # 通义API自然语言转SQL模块
├── pyproject.toml         # Python依赖管理
├── logs/
│   └── query.log          # 查询日志
└── .venv/                 # 推荐的Python虚拟环境
```

---

## 环境准备

1. **Python 版本**  
   推荐 Python 3.8 及以上（项目 pyproject.toml 要求 >=3.12.2）

2. **依赖安装**  
   建议使用虚拟环境：
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   pip install -r requirements.txt  # 或手动安装下方依赖
   ```
   或根据 pyproject.toml 手动安装：
   ```bash
   pip install mysqlclient streamlit requests
   ```

3. **数据库准备**  
   - 使用MySQL数据库，确保已创建好相关表结构。
   - 在项目根目录下创建 `.env` 文件，内容如下（请根据实际情况填写）：
     ```
     DB_HOST=localhost
     DB_USER=你的用户名
     DB_PASSWORD=你的密码
     DB_NAME=你的数据库名
     DB_PORT=3306
     ```

4. **通义API Key**  
   - 已在 `tongyi_api_nl2sql.py` 中配置，如需更换请修改该文件中的 `API_KEY`。

---

## 启动方式

### 1. 启动MCP服务

```bash
python main.py
```
- MCP服务会在8000端口启动，提供 `/schema`、`/query`、`/logs` 等接口。
- 所有数据库操作、日志记录、SQL安全控制均在此服务中完成。

### 2. 命令行主菜单（CLI）

另开一个终端，运行：
```bash
python cli_app_main.py
```
- 支持主菜单选择：自然语言查询、显示所有表结构、按表名查结构。
- 查询结果自动分页，支持next/exit/quit等交互指令。

### 3. 可视化界面（Streamlit GUI）

```bash
streamlit run gui_app.py
```
- 浏览器访问 Streamlit 提供的本地地址（如 http://localhost:8501 ）
- 支持自然语言查询、表结构浏览、单表结构查询，结果以表格形式展示。

---

## 日志与安全

- 所有SQL查询及时间戳会记录在 `logs/query.log`，可通过 `/logs` 接口或直接查看文件获取。
- MCP服务内置只读SQL白名单、敏感字段过滤（如password、salary）、SQL注入防御等安全机制。

---

## 主要功能

- **自然语言转SQL**：集成通义大模型API，支持复杂查询意图的SQL自动生成
- **数据库结构浏览**：支持全库和单表结构可视化
- **查询结果分页**：CLI端自动分页，GUI端表格滚动
- **安全防护**：只读SQL、敏感字段拦截、SQL注入检测
- **日志记录**：所有查询均有日志可查

---

## 常见问题

- **无法连接数据库**：请检查.env配置和MySQL服务状态
- **通义API调用失败**：请检查API Key和网络
- **查询被拦截**：请确认SQL为只读且未涉及敏感字段或注入特征

---

## 致谢

- 通义大模型API
- Streamlit
- MCP开源组件

---

如需进一步定制或遇到问题，欢迎联系作者：唐镱航
