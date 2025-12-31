#!/usr/bin/env python3
"""
快速测试 arXiv 集成功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入我们的模块
from arxiv_fetcher import ArxivFetcher
from arxiv_to_csv import ArxivToCSV

def test_arxiv_fetch():
    """测试 arXiv 获取功能"""
    print("🧪 测试 arXiv 获取功能")
    print("-" * 40)

    try:
        fetcher = ArxivFetcher(delay_seconds=2)
        papers = fetcher.fetch_latest_papers(
            categories=["cs.AI"],
            max_results=3
        )

        if papers:
            print(f"✅ 成功获取 {len(papers)} 篇论文")
            for i, paper in enumerate(papers[:2], 1):
                print(f"\n{i}. 标题: {paper['title'][:60]}...")
                print(f"   作者: {', '.join(paper['authors'][:2])}{' 等' if len(paper['authors']) > 2 else ''}")
                print(f"   类别: {', '.join(paper['categories'][:3])}")
                print(f"   arXiv ID: {paper.get('arxiv_id', 'N/A')}")
        else:
            print("❌ 未获取到论文")
            return False

    except Exception as e:
        print(f"❌ 获取出错: {e}")
        return False

    return True

def test_csv_save():
    """测试 CSV 保存功能"""
    print("\n🧪 测试 CSV 保存功能")
    print("-" * 40)

    try:
        # 获取一篇论文
        fetcher = ArxivFetcher(delay_seconds=2)
        papers = fetcher.fetch_latest_papers(
            categories=["cs.CL"],
            max_results=1
        )

        if papers:
            # 保存到测试 CSV
            csv_saver = ArxivToCSV("test_arxiv_papers.csv")
            csv_saver.save_to_csv(papers, append_mode=True)

            # 读取验证
            saved_papers = csv_saver.load_from_csv()
            if saved_papers:
                print(f"✅ 成功保存和加载 {len(saved_papers)} 篇论文")
                print(f"   文件: test_arxiv_papers.csv")
                return True
            else:
                print("❌ 保存后读取失败")
                return False
        else:
            print("❌ 无法获取测试论文")
            return False

    except Exception as e:
        print(f"❌ CSV 操作出错: {e}")
        return False

def test_search():
    """测试搜索功能"""
    print("\n🧪 测试搜索功能")
    print("-" * 40)

    try:
        fetcher = ArxivFetcher(delay_seconds=2)
        papers = fetcher.search_papers(
            query="machine learning",
            max_results=2
        )

        if papers:
            print(f"✅ 搜索成功，找到 {len(papers)} 篇论文")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper['title'][:50]}...")
        else:
            print("❌ 搜索未找到结果")
            return False

    except Exception as e:
        print(f"❌ 搜索出错: {e}")
        return False

    return True

def test_feishu_config():
    """测试飞书配置"""
    print("\n🧪 测试飞书配置")
    print("-" * 40)

    FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
    FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")

    if not FEISHU_APP_ID:
        print("❌ FEISHU_APP_ID 未配置")
        return False

    if not FEISHU_APP_SECRET:
        print("❌ FEISHU_APP_SECRET 未配置")
        return False

    print(f"✅ 飞书配置正常")
    print(f"   App ID: {FEISHU_APP_ID}")
    print(f"   App Secret: {FEISHU_APP_SECRET[:10]}...")

    return True

def cleanup_test_files():
    """清理测试文件"""
    test_files = [
        "test_arxiv_papers.csv",
        "processed_arxiv_ids.txt"
    ]

    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️ 已清理: {file}")
            except:
                pass

def main():
    print("🚀 arXiv 集成功能测试")
    print("=" * 50)

    # 清理之前的测试文件
    cleanup_test_files()

    # 运行测试
    tests = [
        ("arXiv 获取", test_arxiv_fetch),
        ("CSV 保存", test_csv_save),
        ("搜索功能", test_search),
        ("飞书配置", test_feishu_config)
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        results[test_name] = test_func()

    # 显示测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name:15}: {status}")
        if result:
            passed += 1

    print(f"\n📈 测试统计: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！arXiv 集成功能正常")
    else:
        print("⚠️ 部分测试失败，请检查相关配置")

    # 清理测试文件
    cleanup_test_files()

if __name__ == "__main__":
    main()