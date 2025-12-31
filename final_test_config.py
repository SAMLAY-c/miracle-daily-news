#!/usr/bin/env python3
"""
最终配置测试 - 验证所有 arXiv 集成组件
"""

import os
import requests
import time
from dotenv import load_dotenv
from arxiv_fetcher import ArxivFetcher

# 加载环境变量
load_dotenv()

def print_config_summary():
    """打印配置总结"""
    print("🔧 当前配置验证")
    print("=" * 50)

    # 飞书配置
    print("📱 飞书应用配置:")
    feishu_app_id = os.getenv("FEISHU_APP_ID", 'N/A')
    feishu_app_secret = os.getenv("FEISHU_APP_SECRET", 'N/A')[:20] + "..."
    feishu_app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN", 'N/A')
    feishu_table_id = os.getenv("FEISHU_BITABLE_TABLE_ID", 'N/A')

    print(f"   App ID: {feishu_app_id}")
    print(f"   App Secret: {feishu_app_secret}")
    print(f"   App Token: {feishu_app_token}")
    print(f"   Table ID: {feishu_table_id}")
    print()

    # AI 配置
    print("🤖 AI 模型配置:")
    silicon_key = os.getenv("SILICON_KEY", 'N/A')[:30] + "..."
    print(f"   SiliconFlow Key: {silicon_key}")
    print(f"   模型: {os.getenv('MODEL_NAME', 'N/A')}")
    print()

    # arXiv 配置
    print("📚 arXiv 配置:")
    arxiv_limit = os.getenv("ARXIV_LIMIT", 'N/A')
    arxiv_categories = os.getenv("ARXIV_CATEGORIES", 'N/A')
    print(f"   默认数量: {arxiv_limit}")
    print(f"   默认类别: {arxiv_categories}")
    print()

def test_feishu_token():
    """测试飞书认证"""
    print("\n🔐 测试飞书认证...")

    if not all([
        os.getenv("FEISHU_APP_ID"),
        os.getenv("FEISHU_APP_SECRET"),
        os.getenv("FEISHU_BITABLE_APP_TOKEN"),
        os.getenv("FEISHU_BITABLE_TABLE_ID")
    ]):
        print("❌ 配置不完整，请检查 .env 文件")
        return False

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": os.getenv("FEISHU_APP_ID"),
        "app_secret": os.getenv("FEISHU_APP_SECRET")
    }

    try:
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            token = resp.json().get("tenant_access_token")
            print("✅ 飞书认证成功")
            return token
        else:
            print(f"❌ 飞书认证失败: {resp.text}")
            return None
    except Exception as e:
        print(f"❌ 网络请求错误: {e}")
        return None

def test_arxiv_fetcher():
    """测试 arXiv 获取器"""
    print("\n📚 测试 arXiv 获取器...")

    try:
        fetcher = ArxivFetcher(delay_seconds=2)
        papers = fetcher.fetch_latest_papers(
            categories=["cs.AI"],
            max_results=2
        )

        if papers:
            print(f"✅ arXiv 获取成功: {len(papers)} 篇")
            for i, paper in enumerate(papers, 1):
                print(f"   {i}. {paper.get('title', 'N/A')[:50]}...")
            return True
        else:
            print("❌ arXiv 获取失败")
            return False

    except Exception as e:
        print(f"❌ arXiv 获取器错误: {e}")
        return False

def test_feishu_fields(token):
    """测试飞书字段"""
    print("\n📋 测试飞书字段...")

    if not token:
        print("❌ 需要 token 来测试字段")
        return False

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{os.getenv('FEISHU_BITABLE_APP_TOKEN')}/tables/{os.getenv('FEISHU_BITABLE_TABLE_ID')}/fields"
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
                print(f"✅ 字段获取成功: {len(fields)} 个")
                return True
            else:
                print(f"❌ 字段获取失败: {result.get('msg')}")
                return False
        else:
            print(f"❌ 请求失败: {resp.text}")
            return False

    except Exception as e:
        print(f"❌ 字段测试错误: {e}")
        return False

def test_feishu_write(token):
    """测试飞书写入"""
    print("\n✍️ 测试飞书写入...")

    if not token:
        print("❌ 需要 token 来测试写入")
        return False

    # 构造测试记录
    test_record = {
        "fields": {
            "fldRJ6ZXT2": int(time.time() * 1000),  # 收藏日期
            "fldQySf922": "测试 arXiv 论文标题",  # 新闻标题
            "fldhcSKytX": int(time.time() * 1000),  # 发布日期
            "fld0fcfgz0": "https://arxiv.org/abs/2312.12345",  # 原文链接
            "fld7j1isdW": 0,  # HN热度
            "fldkkjQi8y": "生成式AI",  # 所属领域
            "fldom51JuS": "这是一个测试的技术摘要",  # 一句话摘要
            "fld0RXbCrS": "这是测试的创新点描述",  # 底层逻辑
            "fld0vyHCr2": "这是测试的影响评估",  # 潜在影响
            "fldwYrkaCR": "👀 重要进展",  # AI推荐
            "fldhwToUil": 4  # 商业潜力
        }
    }

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{os.getenv('FEISHU_BITABLE_APP_TOKEN')}/tables/{os.getenv('FEISHU_BITABLE_TABLE_ID')}/records/batch_create"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, headers=headers, json=test_record)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 0:
                print("✅ 飞书写入测试成功")
                return True
            else:
                print(f"❌ 飞书写入失败: {result.get('msg')}")
                return False
        else:
            print(f"❌ 写入请求失败: {resp.text}")
            return False

    except Exception as e:
        print(f"❌ 写入测试错误: {e}")
        return False

def main():
    print("🧪 arXiv 集成系统最终测试")
    print("=" * 50)

    # 1. 配置总结
    print_config_summary()

    # 2. 飞书认证测试
    token = test_feishu_token()

    if not token:
        print("\n❌ 配置测试失败，请检查以下配置:")
        print("   1. 飞书 App ID 和 App Secret")
        print("   2. 飞书多维表格权限")
        print("   3. 网络连接")
        return

    # 3. arXiv 获取器测试
    if not test_arxiv_fetcher():
        print("\n❌ arXiv 获取器测试失败")
        return

    # 4. 飞书字段测试
    if not test_feishu_fields(token):
        print("\n❌ 飞书字段测试失败")
        return

    # 5. 飞书写入测试
    if not test_feishu_write(token):
        print("\n❌ 飞书写入测试失败")
        return

    print("\n🎉 所有测试通过！系统配置正确")

    # 6. 多维表格链接
    app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN")
    table_id = os.getenv("FEISHU_BITABLE_TABLE_ID")
    print(f"\n📱 多维表格链接:")
    print(f"   https://pcnlp18cy9bm.feishu.cn/base/{app_token}?table={table_id}")

if __name__ == "__main__":
    main()