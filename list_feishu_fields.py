#!/usr/bin/env python3
"""
查看飞书多维表格的字段信息
"""

import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 飞书配置
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
FEISHU_BITABLE_APP_TOKEN = os.getenv("FEISHU_BITABLE_APP_TOKEN")
FEISHU_BITABLE_TABLE_ID = os.getenv("FEISHU_BITABLE_TABLE_ID")

def get_tenant_token():
    """获取飞书访问凭证"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}

    try:
        resp = requests.post(url, json=payload)
        if resp.status_code != 200:
            print(f"❌ Token 获取失败: {resp.text}")
            return None
        return resp.json().get("tenant_access_token")
    except Exception as e:
        print(f"❌ 网络请求错误: {e}")
        return None

def list_table_fields(token):
    """列出表格的字段"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BITABLE_APP_TOKEN}/tables/{FEISHU_BITABLE_TABLE_ID}/fields"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 0:
                fields = result.get("data", {}).get("items", [])
                return fields
            else:
                print(f"❌ 字段获取失败: {result.get('msg')}")
                return None
        else:
            print(f"❌ 请求失败: {resp.text}")
            return None
    except Exception as e:
        print(f"❌ 请求出错: {e}")
        return None

def main():
    print("🔍 查看飞书多维表格字段")
    print("=" * 50)

    token = get_tenant_token()
    if not token:
        print("❌ 无法获取访问凭证")
        return

    fields = list_table_fields(token)
    if fields is not None:
        print(f"📋 多维表格字段列表 (共 {len(fields)} 个字段):")
        print("-" * 80)

        for i, field in enumerate(fields, 1):
            field_name = field.get("field_name", "未知")
            field_type = field.get("type", "未知")
            field_id = field.get("field_id", "未知")
            is_primary = "是" if field.get("is_primary") else "否"
            description = field.get("description", "")

            print(f"{i:2d}. {field_name}")
            print(f"     字段ID: {field_id}")
            print(f"     类型: {field_type}")
            print(f"     是主键: {is_primary}")
            if description:
                print(f"     描述: {description}")
            print()

        # 显示字段映射建议
        print("📝 字段映射建议:")
        print("-" * 40)
        field_mapping = {
            "新闻标题": "news_title",
            "论文标题": "paper_title",
            "一句话摘要": "summary",
            "所属领域": "category",
            "底层逻辑": "reason",
            "潜在影响": "impact",
            "技术创新性": "innovation",
            "实用性评估": "practicality",
            "商业潜力": "commercial_score",
            "商业落地潜力": "commercial_score",
            "AI推荐": "recommendation",
            "HN热度": "hn_score",
            "发布日期": "published_date",
            "收藏日期": "saved_date",
            "原文链接": "source_url",
            "PDF链接": "pdf_url"
        }

        for field in fields:
            field_name = field.get("field_name", "")
            if field_name in field_mapping:
                print(f"   {field_name} -> {field_mapping[field_name]}")

if __name__ == "__main__":
    main()