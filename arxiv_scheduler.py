#!/usr/bin/env python3
"""
arXiv 论文定时获取脚本
可以定期运行，自动获取最新论文并保存到 CSV
"""

import os
import sys
import argparse
from datetime import datetime
from arxiv_to_csv import ArxivToCSV, fetch_and_save_papers

def print_banner():
    """打印程序标题"""
    print("🚀 arXiv 论文定时获取器")
    print("=" * 50)
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def fetch_by_category(categories: list, max_papers: int, csv_file: str):
    """按类别获取论文"""
    print(f"📚 获取类别: {', '.join(categories)}")
    print(f"📊 最大数量: {max_papers}")

    fetch_and_save_papers(
        categories=categories,
        max_results=max_papers,
        csv_filename=csv_file
    )

def search_and_save(keyword: str, max_papers: int, csv_file: str):
    """搜索特定关键词的论文"""
    from arxiv_fetcher import ArxivFetcher

    print(f"🔍 搜索关键词: {keyword}")
    print(f"📊 最大数量: {max_papers}")

    fetcher = ArxivFetcher(delay_seconds=2)
    papers = fetcher.search_papers(
        query=keyword,
        max_results=max_papers,
        sort_by="submittedDate"
    )

    if papers:
        # 为搜索的论文添加 arxiv_id
        for paper in papers:
            if 'arxiv_id' not in paper and 'id' in paper:
                # 从 URL 中提取 arxiv_id
                import re
                match = re.search(r'arxiv\.org/abs/(\d+\.\d+)', paper['id'])
                if match:
                    paper['arxiv_id'] = match.group(1)

        csv_saver = ArxivToCSV(csv_file)
        csv_saver.save_to_csv(papers, append_mode=True)
    else:
        print("❌ 未找到相关论文")

def show_statistics(csv_file: str):
    """显示 CSV 文件统计信息"""
    csv_saver = ArxivToCSV(csv_file)
    stats = csv_saver.get_statistics()

    print(f"📊 {csv_file} 统计信息:")
    print(f"   总论文数: {stats['total_papers']}")

    if stats.get('categories'):
        print("   类别分布:")
        for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"     {category}: {count}")

    if stats.get('years'):
        print("   年份分布:")
        for year, count in sorted(stats['years'].items()):
            print(f"     {year}: {count}")

    if stats.get('latest_fetch'):
        print(f"   最后获取: {stats['latest_fetch']}")

def search_in_csv(keyword: str, csv_file: str):
    """在 CSV 中搜索论文"""
    csv_saver = ArxivToCSV(csv_file)
    results = csv_saver.search_in_csv(keyword)

    if results:
        print(f"🔍 找到 {len(results)} 篇相关论文:")
        print("-" * 80)
        for i, paper in enumerate(results[:10], 1):  # 只显示前10篇
            print(f"{i:2d}. {paper['title'][:70]}...")
            authors = paper['authors'][:2] if paper['authors'] else []
            author_str = ', '.join(authors) + (' 等' if len(paper['authors']) > 2 else '')
            print(f"     作者: {author_str}")
            print(f"     日期: {paper['published'][:10] if paper['published'] else '未知'}")
            print(f"     链接: {paper.get('source_url', '无')}")
            print()
    else:
        print(f"🔍 未找到包含 '{keyword}' 的论文")

def export_to_markdown(csv_file: str, output_file: str = None):
    """导出 CSV 数据到 Markdown 文件"""
    if not output_file:
        output_file = csv_file.replace('.csv', '_export.md')

    csv_saver = ArxivToCSV(csv_file)
    papers = csv_saver.load_from_csv()

    if not papers:
        print("❌ 没有数据可导出")
        return

    # 按发布时间排序
    papers.sort(key=lambda x: x.get('published', ''), reverse=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# arXiv 论文集\n\n")
        f.write(f"*导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        f.write(f"*总计论文数: {len(papers)}*\n\n")

        # 按类别分组
        categories = {}
        for paper in papers:
            for category in paper['categories']:
                if category not in categories:
                    categories[category] = []
                categories[category].append(paper)

        for category, category_papers in sorted(categories.items()):
            f.write(f"## {category} ({len(category_papers)} 篇)\n\n")

            for paper in category_papers[:5]:  # 每个类别最多显示5篇
                f.write(f"### {paper['title']}\n\n")
                f.write(f"**作者:** {', '.join(paper['authors'][:3])}{' 等' if len(paper['authors']) > 3 else ''}\n\n")
                f.write(f"**摘要:** {paper['summary'][:200]}{'...' if len(paper['summary']) > 200 else ''}\n\n")
                f.write(f"**链接:** [arXiv]({paper.get('source_url', '无')})")
                if paper.get('pdf_url'):
                    f.write(f" | [PDF]({paper['pdf_url']})")
                f.write(f"\n\n")
                f.write("---\n\n")

    print(f"✅ 成功导出到 {output_file}")

def main():
    parser = argparse.ArgumentParser(description='arXiv 论文定时获取和管理工具')
    parser.add_argument('--categories', '-c',
                       default='cs.CV,cs.AI,cs.LG',
                       help='论文类别，用逗号分隔 (默认: cs.CV,cs.AI,cs.LG)')
    parser.add_argument('--max-papers', '-m',
                       type=int, default=20,
                       help='最大获取论文数 (默认: 20)')
    parser.add_argument('--csv-file', '-f',
                       default='arxiv_papers.csv',
                       help='CSV 文件名 (默认: arxiv_papers.csv)')
    parser.add_argument('--search', '-s',
                       help='搜索关键词')
    parser.add_argument('--stats', action='store_true',
                       help='显示统计信息')
    parser.add_argument('--search-csv',
                       help='在 CSV 文件中搜索')
    parser.add_argument('--export-markdown',
                       help='导出到 Markdown 文件')

    args = parser.parse_args()

    print_banner()

    try:
        if args.stats:
            show_statistics(args.csv_file)

        elif args.search_csv:
            search_in_csv(args.search_csv, args.csv_file)

        elif args.export_markdown:
            export_to_markdown(args.csv_file, args.export_markdown)

        elif args.search:
            search_and_save(args.search, args.max_papers, args.csv_file)

        else:
            # 默认行为：按类别获取论文
            categories = [cat.strip() for cat in args.categories.split(',')]
            fetch_by_category(categories, args.max_papers, args.csv_file)

            # 显示最终统计
            print("\n" + "=" * 50)
            show_statistics(args.csv_file)

    except KeyboardInterrupt:
        print("\n⏹️  用户中断程序")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()