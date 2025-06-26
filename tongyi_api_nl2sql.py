import requests
import json

API_KEY = "sk-bdc3b0de61364bad8bd6944e2394907b"
API_URL = " https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

SYSTEM_PROMPT = "你是一个SQL专家。根据用户输入和数据库结构，生成对应的MySQL SQL语句，只返回SQL语句本身。"

def nl2sql(nl_query: str, schema: dict) -> str:
    schema_str = json.dumps(schema, ensure_ascii=False)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-turbo",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT + f"\n数据库结构: {schema_str}"},
            {"role": "user", "content": nl_query}
        ]
    }
    response = requests.post(API_URL.strip(), headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        # 假设返回格式为{"choices": [{"message": {"content": "..."}}]}
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    else:
        raise Exception(f"通义API请求失败: {response.status_code}, {response.text}") 