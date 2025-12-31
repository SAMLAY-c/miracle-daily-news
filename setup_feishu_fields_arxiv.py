#!/usr/bin/env python3
"""
飞书多维表格字段设置 - arXiv 论文版
用于创建和配置飞书多维表格字段，支持 arXiv 论文数据的结构化存储
"""

import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 飞书配置
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", 'cli_a9a5b41b8abf1ced')
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", 'M8azGTlTa9Aqwv19fdUZwge714CqFWD1')

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

def create_arxiv_table(token):
    """创建 arXiv 论文专用多维表格"""
    url = "https://open.feishu.cn/open-apis/bitable/v1/apps"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    app_data = {
        "name": "arXiv 论文库",
        "folder": "",
        "time_zone": "Asia/Shanghai"
    }

    try:
        resp = requests.post(url, headers=headers, json=app_data)
        if resp.status_code == 200:
            result = resp.json()
            app_token = result.get("data", {}).get("app", {}).get("app_token")
            print(f"✅ 创建成功！App Token: {app_token}")
            return app_token
        else:
            print(f"❌ 创建失败: {resp.text}")
            return None
    except Exception as e:
        print(f"❌ 创建出错: {e}")
        return None

def setup_arxiv_fields(token, app_token):
    """设置 arXiv 论文表格字段"""
    # 创建数据表
    table_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    table_data = {
        "table": {
            "name": "论文库",
            "default_view_id": "",
            "revision": 1
        }
    }

    try:
        resp = requests.post(table_url, headers=headers, json=table_data)
        if resp.status_code == 200:
            result = resp.json()
            table_id = result.get("data", {}).get("table", {}).get("table_id")
            print(f"✅ 表格创建成功！Table ID: {table_id}")
            return table_id
        else:
            print(f"❌ 表格创建失败: {resp.text}")
            return None
    except Exception as e:
        print(f"❌ 表格创建出错: {e}")
        return None

def create_arxiv_fields(token, app_token, table_id):
    """创建 arXiv 论文专用字段"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields/batch_create"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # arXiv 论文专用字段定义
    fields = [
        {
            "field_name": "论文标题",
            "type": 1,  # 文本
            "is_primary": True,
            "description": "arXiv 论文标题"
        },
        {
            "field_name": "arxiv_id",
            "type": 1,  # 文本
            "is_primary": False,
            "description": "arXiv 论文唯一标识 (如: 2312.12345)"
        },
        {
            "field_name": "作者列表",
            "type": 1,  # 文本
            "is_primary": False,
            "description": "论文作者，用分号分隔"
        },
        {
            "field_name": "技术贡献摘要",
            "type": 1,  # 文本
            "is_primary": False,
            "description": "AI 分析的技术贡献摘要"
        },
        {
            "field_name": "所属领域",
            "type": 4,  # 单选
            "is_primary": False,
            "property": {
                "options": [
                    {"name": "Generative AI"},
                    {"name": "计算机视觉"},
                    {"name": "自然语言处理"},
                    {"name": "机器学习"},
                    {"name": "强化学习"},
                    {"name": "其他"}
                ]
            }
        },
        {
            "field_name": "技术创新性",
            "type": 1,  # 文本
            "is_primary": False,
            "description": "AI 评估的核心创新点"
        },
        {
            "field_name": "实用性评估",
            "type": 1,  # 文本
            "is_primary": False,
            "description": "技术落地的可行性和难度评估"
        },
        {
            "field_name": "商业潜力",
            "type": 7,  # 数字 (评分1-5)
            "is_primary": False,
            "description": "AI 评估的商业潜力评分 (1-5分)"
        },
        {
            "field_name": "AI推荐",
            "type": 4,  # 单选
            "is_primary": False,
            "property": {
                "options": [
                    {"name": "🔥 重大突破"},
                    {"name": "👀 重要进展"},
                    {"name": "☕️ 学术价值"}
                ]
            }
        },
        {
            "field_name": "论文摘要",
            "type": 1,  # 文本
            "is_primary": False,
            "description": "原始论文摘要"
        },
        {
            "field_name": "arxiv分类",
            "type": 1,  # 文本
            "is_primary": False,
            "description": "arXiv 官方分类 (如: cs.CV, cs.AI)"
        },
        {
            "field_name": "发布日期",
            "type": 5,  # 日期
            "is_primary": False,
            "description": "论文发布日期"
        },
        {
            "field_name": "更新日期",
            "type": 5,  # 日期
            "is_primary": False,
            "description": "论文最后更新日期"
        },
        {
            "field_name": "收藏日期",
            "type": 5,  # 日期
            "is_primary": False,
            "description": "论文收录到表格的日期"
        },
        {
            "field_name": "论文链接",
            "type": 21,  # 超链接
            "is_primary": False,
            "description": "arXiv 原文链接"
        },
        {
            "field_name": "PDF链接",
            "type": 21,  # 超链接
            "is_primary": False,
            "description": "PDF 下载链接"
        },
        {
            "field_name": "数据来源",
            "type": 4,  # 单选
            "is_primary": False,
            "property": {
                "options": [
                    {"name": "arxiv"},
                    {"name": "Hacker News"},
                    {"name": "其他"}
                ]
            }
        }
    ]

    payload = {"fields": fields}

    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ 字段创建成功！创建了 {len(fields)} 个字段")

            # 显示创建的字段
            print("\n📋 创建的字段列表:")
            for i, field in enumerate(fields, 1):
                field_type = {
                    1: "文本", 4: "单选", 5: "日期",
                    7: "数字", 21: "超链接"
                }.get(field["type"], "未知")
                print(f"   {i:2d}. {field['field_name']} ({field_type})")

            return True
        else:
            print(f"❌ 字段创建失败: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ 字段创建出错: {e}")
        return False

def generate_instructions(app_token, table_id):
    """生成配置说明"""
    print("\n" + "="*60)
    print("🎉 arXiv 论文多维表格配置完成！")
    print("="*60)
    print(f"📱 多维表格链接:")
    print(f"   https://pcnlp18cy9bm.feishu.cn/base/{app_token}?table={table_id}")
    print()
    print("⚙️ 环境变量配置:")
    print(f"   FEISHU_BITABLE_APP_TOKEN='{app_token}'")
    print(f"   FEISHU_BITABLE_TABLE_ID='{table_id}'")
    print()
    print("📝 字段说明:")
    print("   • 论文标题: arXiv 论文的完整标题")
    print("   • arxiv_id: 论文唯一标识符")
    print("   • 技术贡献摘要: AI 分析的50字摘要")
    print("   • 所属领域: AI 评估的论文领域分类")
    print("   • 技术创新性: 核心创新点评估")
    print("   • 实用性评估: 技术落地可行性分析")
    print("   • 商业潜力: 1-5分商业潜力评分")
    print("   • AI推荐: AI 给出的推荐等级")
    print("   • 论文链接: arXiv 原文链接")
    print("   • PDF链接: 论文PDF下载链接")
    print()
    print("🚀 使用方法:")
    print("   python3 hacker_news_feishu_final.py")
    print()
    print("📊 字段映射关系已自动配置，程序会正确写入对应字段")

def main():
    print("🔧 arXiv 论文多维表格字段设置工具")
    print("=" * 50)

    # 1. 获取访问凭证
    print("🔐 正在获取飞书访问凭证...")
    token = get_tenant_token()

    if not token:
        print("❌ 无法获取访问凭证，请检查 App ID 和 App Secret")
        return

    print("✅ 访问凭证获取成功")

    # 2. 询问用户选择
    print("\n🎯 请选择操作:")
    print("   1. 创建新的 arXiv 论文多维表格")
    print("   2. 为现有表格添加字段 (需要 App Token)")

    choice = input("\n请输入选择 (1/2): ").strip()

    if choice == "1":
        # 创建新表格
        print("\n📊 正在创建新的多维表格...")
        app_token = create_arxiv_table(token)

        if app_token:
            print("\n🏗️ 正在创建数据表...")
            table_id = setup_arxiv_fields(token, app_token)

            if table_id:
                print("\n📝 正在创建字段...")
                if create_arxiv_fields(token, app_token, table_id):
                    generate_instructions(app_token, table_id)

    elif choice == "2":
        # 为现有表格添加字段
        app_token = input("\n请输入 App Token: ").strip()
        table_id = input("请输入 Table ID: ").strip()

        print(f"\n📝 正在为现有表格创建字段...")
        if create_arxiv_fields(token, app_token, table_id):
            generate_instructions(app_token, table_id)

    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()