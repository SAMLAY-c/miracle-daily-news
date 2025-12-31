#!/usr/bin/env python3
"""
调试飞书多维表格 API
"""

import requests
import os
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 飞书配置
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
FEISHU_BITABLE_APP_TOKEN = os.getenv("FEISHU_BITABLE_APP_TOKEN")
FEISHU_TABLE_ID = os.getenv("FEISHU_BITABLE_TABLE_ID")

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

def test_single_record(token):
    """测试单条记录写入"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BITABLE_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 使用正确的字段ID
    fields = {
        "fldRJ6ZXT2": int(time.time() * 1000),  # 收藏日期
        "fldQySf922": "测试论文标题",  # 新闻标题
        "fldhcSKytX": int(time.time() * 1000),  # 发布日期
        "fld0fcfgz0": "https://arxiv.org/abs/2312.12345",  # 原文链接
        "fld7j1isdW": 0,  # HN热度
        "fldkkjQi8y": "生成式AI",  # 所属领域
        "fldom51JuS": "这是一个测试摘要",  # 一句话摘要
        "fld0RXbCrS": "这是一个测试的技术创新描述",  # 底层逻辑
        "fld0vyHCr2": "这是一个测试的影响评估",  # 潜在影响
        "fldwYrkaCR": "👀 重要进展",  # AI推荐
        "fldhwToUil": 4  # 商业潜力
    }

    payload = {"fields": fields}

    try:
        resp = requests.post(url, headers=headers, json=payload)
        print(f"状态码: {resp.status_code}")
        print(f"响应内容: {resp.text}")

        if resp.status_code == 200:
            result = resp.json()
            print(f"写入结果: {result}")
            return result
        else:
            print(f"写入失败: {resp.text}")
            return None

    except Exception as e:
        print(f"请求出错: {e}")
        return None

def main():
    print("🔧 调试飞书多维表格 API")
    print("=" * 50)

    token = get_tenant_token()
    if not token:
        print("❌ 无法获取访问凭证")
        return

    print("✅ 访问凭证获取成功")
    print("📝 测试单条记录写入...")

    result = test_single_record(token)

if __name__ == "__main__":
    main()