"""
飞书多维表格字段创建工具
运行此脚本会自动创建所有必需的字段
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
APP_ID = os.getenv("FEISHU_APP_ID", "cli_a9a694741d38dbd7")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "UenXmsnXoKjyQVh5arXtBcyAoneKudgI")
BITABLE_APP_TOKEN = os.getenv("FEISHU_BITABLE_APP_TOKEN", "Cprlb3kZFaBOyNsleepcdSAJnN5")
TABLE_ID = os.getenv("FEISHU_BITABLE_TABLE_ID", "tblS7Lr8KRKHYBDo")

def get_token():
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    resp = requests.post(url, json=data)
    if resp.status_code == 200 and "tenant_access_token" in resp.json():
        return resp.json()["tenant_access_token"]
    else:
        raise Exception(f"获取 Token 失败: {resp.text}")

def create_field(token, field_config):
    """创建字段"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    resp = requests.post(url, headers=headers, json=field_config)
    res_json = resp.json()

    if res_json.get("code") == 0:
        print(f"✅ 字段 [{field_config['field_name']}] 创建成功")
        return True
    else:
        error_msg = res_json.get('msg', '未知错误')
        if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
            print(f"ℹ️  字段 [{field_config['field_name']}] 已存在")
            return True
        else:
            print(f"❌ 字段 [{field_config['field_name']}] 创建失败: {error_msg}")
            return False

if __name__ == "__main__":
    print("🏗️  飞书表格字段创建工具")
    print(f"📋 目标表格: https://pcnlp18cy9bm.feishu.cn/base/{BITABLE_APP_TOKEN}?table={TABLE_ID}")
    print("=" * 60)

    try:
        print("🔑 正在获取访问令牌...")
        access_token = get_token()
        print("✅ Token 获取成功！")
        print()
        print("🏗️  开始创建字段...\n")

        # 定义所有需要的字段
        fields_to_create = [
            {
                "field_name": "新闻标题",
                "type": 1  # 多行文本
            },
            {
                "field_name": "发布日期",
                "type": 5,  # 日期
                "property": {
                    "date_formatter": "yyyy/MM/dd HH:mm"
                }
            },
            {
                "field_name": "原文链接",
                "type": 15  # 超链接
            },
            {
                "field_name": "HN热度",
                "type": 2,  # 数字
                "property": {
                    "formatter": "0"
                }
            },
            {
                "field_name": "所属领域",
                "type": 3,  # 单选
                "property": {
                    "options": [
                        {"name": "Generative AI"},
                        {"name": "SaaS"},
                        {"name": "硬科技"},
                        {"name": "开发工具"},
                        {"name": "Web3"},
                        {"name": "生物科技"},
                        {"name": "其他"}
                    ]
                }
            },
            {
                "field_name": "一句话摘要",
                "type": 1  # 多行文本
            },
            {
                "field_name": "底层逻辑",
                "type": 1  # 多行文本
            },
            {
                "field_name": "潜在影响",
                "type": 1  # 多行文本
            },
            {
                "field_name": "商业潜力",
                "type": 2,  # 评分
                "ui_type": "Rating",
                "property": {
                    "min": 1,
                    "max": 5,
                    "formatter": "0"
                }
            },
            {
                "field_name": "AI推荐",
                "type": 3,  # 单选
                "property": {
                    "options": [
                        {"name": "🔥 必读"},
                        {"name": "👀 值得关注"},
                        {"name": "☕️ 随便看看"}
                    ]
                }
            },
            {
                "field_name": "收藏日期",
                "type": 5,  # 日期
                "property": {
                    "date_formatter": "yyyy/MM/dd HH:mm"
                }
            }
        ]

        success_count = 0
        total_count = len(fields_to_create)

        for i, field in enumerate(fields_to_create, 1):
            print(f"[{i}/{total_count}] 正在创建字段: {field['field_name']}...")
            if create_field(access_token, field):
                success_count += 1
            time.sleep(1)  # 避免请求过快

        print("\n" + "=" * 60)
        print(f"✨ 字段创建完成！成功: {success_count}/{total_count}")
        print("📝 请刷新飞书表格查看结果")
        print()
        print("🎯 接下来可以运行主程序:")
        print("   python3 hacker_news_feishu_final.py")

    except Exception as e:
        print(f"💥 发生错误: {e}")
        print()
        print("🔧 请检查:")
        print("   1. 飞书应用是否已发布并启用")
        print("   2. 是否已开通 bitable:app:manager 权限")
        print("   3. 是否已将应用添加到多维表格协作中")