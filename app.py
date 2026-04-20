import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- 基础配置 ---
# --- 从环境变量读取配置 ---
NC_BASE_URL = os.getenv("NC_BASE_URL", "http://nocodb:8080")
NC_TOKEN = os.getenv("NC_TOKEN")
BASE_ID = os.getenv("BASE_ID")
TARGET_TABLE_ID = os.getenv("TARGET_TABLE_ID")

# 注意：环境变量读取进来是字符串，ID 通常需要转为整数
try:
    FIXED_TARGET_RECORD_ID = int(os.getenv("FIXED_TARGET_RECORD_ID", "1"))
except ValueError:
    FIXED_TARGET_RECORD_ID = 1

headers = {
    "xc-token": NC_TOKEN,
    "Content-Type": "application/json"
}
def get_column_id_by_name(base_id, table_id, target_column_name):
    """
    通过字段的显示名称获取其在 API 中使用的 ID (title)
    """
    #https://app.nocodb.com/api/v3/meta/bases/{baseId}/tables/{tableId}
    meta_url = f"{NC_BASE_URL}/api/v3/meta/bases/{base_id}/tables/{table_id}"
    
    try:
        response = requests.get(meta_url, headers=headers)
        if response.status_code == 200:
            payload = response.json()
            fields = payload.get("fields")
            # 在返回的列列表中查找匹配的显示名称 (label)
            for col in fields:
                if col.get("title") == target_column_name:
                    # 返回字段标识符，通常是类似 'nc_xxxx' 或 'ColumnID'
                    return col.get("id") 
            print(f"未找到名称为 {target_column_name} 的字段")
        else:
            print(f"获取元数据失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")
    return "_null"

def process_link(payload):
    """通用关联逻辑：将源表 ID 关联到目标表的指定字段"""
    event_type = payload.get("type")
    if event_type != "records.after.insert":
        return jsonify({"status": "ignored"}), 200

    data = payload.get("data", {});
    rows = data.get("rows", [])
    if not rows:
        return jsonify({"status": "no_data"}), 200

    # 1. 拿到源表新产生的 ID
    source_record_id = rows[0].get("Id")
    source_table_id = data.get("table_name", "_null");
    link_field_id = get_column_id_by_name(BASE_ID,TARGET_TABLE_ID, source_table_id)
    #str(os.getenv(f"LINK_FIELD_{source_table_id}"));
    # https://app.nocodb.com/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}
    # 2. 构造 PATCH 请求，修改目标表（B表）的第 1 条记录
    patch_url = f"{NC_BASE_URL}/api/v3/data/{BASE_ID}/{TARGET_TABLE_ID}/links/{link_field_id}/{FIXED_TARGET_RECORD_ID}"
    
    # 3. 根据传入的 link_field_id 进行关联
    link_payload = { 
        "id":str(source_record_id),
        }

    try:
        res = requests.post(patch_url, headers=headers, json=link_payload)
        if res.status_code == 200:
            print(f"[成功] 字段 {link_field_id} 已关联源 ID: {source_record_id}")
            return jsonify({"status": "success"}), 200
        else:
            print(f"[失败] PATCH 出错: code:{res.status_code} {res.text}")
            return jsonify({"status": "error", "msg": res.text}), res.status_code
    except Exception as e:
        print(f"[异常] {e}")
        return jsonify({"status": "exception"}), 500

# --- 路由定义：为每张表定义独立的 Webhook 路径 ---

@app.route('/nocodbwebhook/linkrollup', methods=['POST'])
def webhook_a2026():
    # 假设 A2026 对应字段 ID: cbtt8iets0ukc07
    return process_link(request.json)

# @app.route('/nocodbwebhook/sa2026', methods=['ddOST'])
# def webhook_sa2026():
#     # 假设 SA2026 对应另一个字段 ID
#     return process_link(request.json, "croguwkyp3584wc")

# @app.route('/nocodbwebhook/fg2026', methods=['POST'])
# def webhook_fg2026():
#     # 假设 FG2026 对应另一个字段 ID
#     return process_link(request.json, "cg5nnxa4fyb8h7c")

if __name__ == '__main__':
    # 监听 5000 端口
    app.run(host='0.0.0.0', port=5000)