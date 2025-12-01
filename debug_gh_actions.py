#!/usr/bin/env python3
"""
调试 GitHub Actions 运行问题的脚本
"""

import os
import json
from dotenv import load_dotenv

def check_env_variables():
    """检查环境变量是否正确设置"""
    print("🔍 检查环境变量设置...")
    print("=" * 50)

    # 加载 .env 文件
    load_dotenv()

    required_vars = [
        'SILICON_KEY',
        'FEISHU_APP_ID',
        'FEISHU_APP_SECRET',
        'FEISHU_BITABLE_APP_TOKEN',
        'FEISHU_BITABLE_TABLE_ID'
    ]

    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if 'SECRET' in var or 'TOKEN' in var or 'KEY' in var:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: 未设置")
            all_good = False

    print("=" * 50)
    if all_good:
        print("✅ 所有必需的环境变量都已设置")
    else:
        print("❌ 部分环境变量缺失，请检查 .env 文件或 GitHub Secrets")

    return all_good

def test_api_connections():
    """测试 API 连接"""
    print("\n🌐 测试 API 连接...")
    print("=" * 50)

    # 测试 SiliconFlow API
    import requests
    try:
        silicon_key = os.getenv("SILICON_KEY")
        if silicon_key:
            headers = {
                "Authorization": f"Bearer {silicon_key}",
                "Content-Type": "application/json"
            }
            response = requests.get("https://api.siliconflow.cn/v1/models", headers=headers, timeout=10)
            if response.status_code == 200:
                print("✅ SiliconFlow API 连接正常")
            else:
                print(f"❌ SiliconFlow API 连接失败: {response.status_code}")
    except Exception as e:
        print(f"❌ SiliconFlow API 测试异常: {e}")

    # 测试飞书 API
    try:
        app_id = os.getenv("FEISHU_APP_ID")
        app_secret = os.getenv("FEISHU_APP_SECRET")
        if app_id and app_secret:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": app_id,
                "app_secret": app_secret
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200 and "tenant_access_token" in response.json():
                print("✅ 飞书 API 连接正常")
            else:
                print(f"❌ 飞书 API 连接失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 飞书 API 测试异常: {e}")

def show_github_secrets_info():
    """显示 GitHub Secrets 设置指南"""
    print("\n📝 GitHub Secrets 设置指南:")
    print("=" * 50)
    print("请在 GitHub 仓库中设置以下 Secrets:")
    print("仓库地址: https://github.com/SAMLAY-c/miracle-daily-news/settings/secrets/actions")
    print()

    secrets_list = [
        ("SILICON_KEY", "你的 SiliconFlow API Key"),
        ("FEISHU_APP_ID", "cli_a9a694741d38dbd7"),
        ("FEISHU_APP_SECRET", "UenXmsnXoKjyQVh5arXtBcyAoneKudgI"),
        ("FEISHU_BITABLE_APP_TOKEN", "Cprlb3kZFaBOyNsleepcdSAJnN5"),
        ("FEISHU_BITABLE_TABLE_ID", "tblS7Lr8KRKHYBDo")
    ]

    for secret_name, example_value in secrets_list:
        print(f"  📌 {secret_name}:")
        print(f"     值: {example_value}")
    print()

def show_workflow_schedule():
    """显示定时任务信息"""
    print("⏰ 定时任务配置:")
    print("=" * 50)
    print("Cron 表达式: '0 0 * * *'")
    print("UTC 时间: 00:00 (午夜)")
    print("北京时间: 08:00 (冬令时) 或 09:00 (夏令时)")
    print()
    print("📅 下次运行时间估算:")
    from datetime import datetime, timedelta, timezone
    import pytz

    # 获取当前 UTC 时间
    now_utc = datetime.now(timezone.utc)
    print(f"   当前 UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")

    # 计算下次运行时间 (今天 UTC 00:00)
    next_run_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    if now_utc.hour >= 0:  # 如果已经过了今天的 00:00，就安排明天
        next_run_utc += timedelta(days=1)

    print(f"   下次运行 UTC: {next_run_utc.strftime('%Y-%m-%d %H:%M:%S')}")

    # 转换为北京时间
    beijing_tz = pytz.timezone('Asia/Shanghai')
    next_run_beijing = next_run_utc.astimezone(beijing_tz)
    print(f"   下次运行北京时间: {next_run_beijing.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("🚀 GitHub Actions 调试工具")
    print("=" * 50)

    # 检查环境变量
    env_ok = check_env_variables()

    # 测试 API 连接
    if env_ok:
        test_api_connections()

    # 显示设置指南
    show_github_secrets_info()

    # 显示定时信息
    show_workflow_schedule()

    print("\n" + "=" * 50)
    print("🎯 解决步骤:")
    print("1. 确保在 GitHub 仓库中设置了所有 Secrets")
    print("2. 去 Actions 页面手动运行一次 workflow 测试")
    print("3. 查看运行日志，定位具体错误")
    print("4. 如果仍然失败，请检查 GitHub Actions 权限设置")