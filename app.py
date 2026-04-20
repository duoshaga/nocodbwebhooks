from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- 基础配置 ---
NC_BASE_URL = "http://nocodb_app:2080"
NC_TOKEN = "你的API_TOKEN"
BASE_ID = "pheeswfbk3ay3et"
TARGET_TABLE_ID = "m7gmgfij532711w" # 目标表 B
FIXED_TARGET_RECORD_ID = 1          # 固定修改 ID 为 1 的记录

headers = {
    "xc-token": NC_TOKEN,
    "Content-Type": "application/json"
}

def process_link(payload, link_field_id):
    """通用关联逻辑：将源表 ID 关联到目标表的指定字段"""
    event_type = payload.get("type")
    if event_type != "records.after.insert":
        return jsonify({"status": "ignored"}), 200

    rows = payload.get("data", {}).get("rows", [])
    if not rows:
        return jsonify({"status": "no_data"}), 200

    # 1. 拿到源表新产生的 ID
    source_record_id = rows[0].get("Id")
    
    # 2. 构造 PATCH 请求，修改目标表（B表）的第 1 条记录
    patch_url = f"{NC_BASE_URL}/api/v3/data/{BASE_ID}/{TARGET_TABLE_ID}/records/{FIXED_TARGET_RECORD_ID}"
    
    # 3. 根据传入的 link_field_id 进行关联
    link_payload = { link_field_id: source_record_id }

    try:
        res = requests.patch(patch_url, headers=headers, json=link_payload)
        if res.status_code == 200:
            print(f"[成功] 字段 {link_field_id} 已关联源 ID: {source_record_id}")
            return jsonify({"status": "success"}), 200
        else:
            print(f"[失败] PATCH 出错: {res.text}")
            return jsonify({"status": "error", "msg": res.text}), 500
    except Exception as e:
        print(f"[异常] {e}")
        return jsonify({"status": "exception"}), 500

# --- 路由定义：为每张表定义独立的 Webhook 路径 ---

@app.route('/webhook/a2026', methods=['POST'])
def webhook_a2026():
    # 假设 A2026 对应字段 ID: cbtt8iets0ukc07
    return process_link(request.json, "cntuakw1olo1uv7")

@app.route('/webhook/sa2026', methods=['POST'])
def webhook_sa2026():
    # 假设 SA2026 对应另一个字段 ID
    return process_link(request.json, "cu7c2kp82nnklc5")

@app.route('/webhook/fg2026', methods=['POST'])
def webhook_fg2026():
    # 假设 FG2026 对应另一个字段 ID
    return process_link(request.json, "cbtt8iets0ukc07")

if __name__ == '__main__':
    # 监听 5000 端口
    app.run(host='0.0.0.0', port=5000)