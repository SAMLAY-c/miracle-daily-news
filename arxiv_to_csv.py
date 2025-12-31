import csv
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from arxiv_fetcher import ArxivFetcher

class ArxivToCSV:
    """arXiv 论文数据 CSV 存储器"""

    def __init__(self, csv_filename: str = "arxiv_papers.csv"):
        """
        初始化 CSV 存储器

        Args:
            csv_filename: CSV 文件名
        """
        self.csv_filename = csv_filename
        self.fieldnames = [
            'arxiv_id',
            'title',
            'authors',
            'summary',
            'published_date',
            'updated_date',
            'categories',
            'pdf_url',
            'source_url',
            'created_at'
        ]
        self._init_csv()

    def _init_csv(self):
        """初始化 CSV 文件，写入表头"""
        if not os.path.exists(self.csv_filename):
            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
            print(f"📁 创建新的 CSV 文件: {self.csv_filename}")

    def _load_existing_ids(self) -> set:
        """加载 CSV 文件中已存在的论文 ID"""
        if not os.path.exists(self.csv_filename):
            return set()

        existing_ids = set()
        try:
            with open(self.csv_filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('arxiv_id'):
                        existing_ids.add(row['arxiv_id'])
        except Exception as e:
            print(f"⚠️ 读取现有 CSV 文件时出错: {e}")
            return set()

        return existing_ids

    def save_to_csv(self, papers: List[Dict], append_mode: bool = True):
        """
        将论文数据保存到 CSV 文件

        Args:
            papers: 论文信息列表
            append_mode: 是否追加模式（True=追加，False=覆盖）
        """
        if not papers:
            print("⚠️ 没有论文数据需要保存")
            return

        # 检查重复
        if append_mode:
            existing_ids = self._load_existing_ids()
            new_papers = []
            duplicate_count = 0

            for paper in papers:
                if paper.get('arxiv_id') not in existing_ids:
                    new_papers.append(paper)
                    existing_ids.add(paper['arxiv_id'])
                else:
                    duplicate_count += 1

            if duplicate_count > 0:
                print(f"📊 跳过 {duplicate_count} 篇重复论文")

            papers = new_papers

        if not papers:
            print("📄 所有论文都已存在，无需保存")
            return

        # 写入 CSV
        mode = 'a' if append_mode else 'w'
        with open(self.csv_filename, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)

            # 如果是覆盖模式或新文件，写入表头
            if mode == 'w' or csvfile.tell() == 0:
                writer.writeheader()

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for paper in papers:
                # 清理和格式化数据
                row = {
                    'arxiv_id': paper.get('arxiv_id', ''),
                    'title': paper.get('title', '').replace('\n', ' ').strip(),
                    'authors': '; '.join(paper.get('authors', [])),
                    'summary': paper.get('summary', '').replace('\n', ' ').strip(),
                    'published_date': paper.get('published', ''),
                    'updated_date': paper.get('updated', ''),
                    'categories': '; '.join(paper.get('categories', [])),
                    'pdf_url': paper.get('pdf_url', ''),
                    'source_url': paper.get('id', ''),
                    'created_at': current_time
                }
                writer.writerow(row)

        print(f"✅ 成功保存 {len(papers)} 篇论文到 {self.csv_filename}")

    def load_from_csv(self) -> List[Dict]:
        """
        从 CSV 文件加载论文数据

        Returns:
            论文信息列表
        """
        if not os.path.exists(self.csv_filename):
            print(f"⚠️ 文件 {self.csv_filename} 不存在")
            return []

        papers = []
        try:
            with open(self.csv_filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # 转换数据格式
                    paper = {
                        'arxiv_id': row.get('arxiv_id', ''),
                        'title': row.get('title', ''),
                        'authors': row.get('authors', '').split('; ') if row.get('authors') else [],
                        'summary': row.get('summary', ''),
                        'published': row.get('published_date', ''),
                        'updated': row.get('updated_date', ''),
                        'categories': row.get('categories', '').split('; ') if row.get('categories') else [],
                        'pdf_url': row.get('pdf_url', ''),
                        'id': row.get('source_url', ''),
                        'created_at': row.get('created_at', '')
                    }
                    papers.append(paper)

            print(f"📖 从 {self.csv_filename} 加载了 {len(papers)} 篇论文")

        except Exception as e:
            print(f"❌ 读取 CSV 文件失败: {e}")

        return papers

    def search_in_csv(self, keyword: str) -> List[Dict]:
        """
        在 CSV 数据中搜索关键词

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的论文列表
        """
        papers = self.load_from_csv()
        if not papers:
            return []

        keyword_lower = keyword.lower()
        matched_papers = []

        for paper in papers:
            # 在标题、摘要、作者、类别中搜索
            search_text = ' '.join([
                paper['title'],
                paper['summary'],
                ' '.join(paper['authors']),
                ' '.join(paper['categories'])
            ]).lower()

            if keyword_lower in search_text:
                matched_papers.append(paper)

        print(f"🔍 搜索 '{keyword}' 找到 {len(matched_papers)} 篇相关论文")
        return matched_papers

    def get_statistics(self) -> Dict:
        """
        获取 CSV 文件的统计信息

        Returns:
            统计信息字典
        """
        if not os.path.exists(self.csv_filename):
            return {"total_papers": 0, "message": "文件不存在"}

        papers = self.load_from_csv()
        if not papers:
            return {"total_papers": 0, "message": "文件为空"}

        # 统计类别分布
        category_count = {}
        for paper in papers:
            for category in paper['categories']:
                category_count[category] = category_count.get(category, 0) + 1

        # 统计时间分布（按年）
        year_count = {}
        for paper in papers:
            if paper['published']:
                try:
                    year = paper['published'][:4]  # 取年份
                    year_count[year] = year_count.get(year, 0) + 1
                except:
                    pass

        return {
            "total_papers": len(papers),
            "categories": category_count,
            "years": year_count,
            "latest_fetch": papers[-1].get('created_at') if papers else None
        }

def fetch_and_save_papers(categories: List[str] = ["cs.CV", "cs.AI", "cs.LG"],
                         max_results: int = 20,
                         csv_filename: str = "arxiv_papers.csv"):
    """
    获取并保存 arXiv 论文到 CSV 的便捷函数

    Args:
        categories: 论文类别列表
        max_results: 最大获取数量
        csv_filename: CSV 文件名
    """
    print("🚀 arXiv 论文自动获取和存储工具")
    print("=" * 50)

    # 创建获取器
    fetcher = ArxivFetcher(delay_seconds=2)

    # 获取最新论文
    print(f"📡 正在获取 arXiv 论文...")
    papers = fetcher.fetch_latest_papers(
        categories=categories,
        max_results=max_results
    )

    if not papers:
        print("❌ 未获取到论文数据")
        return

    # 保存到 CSV
    csv_saver = ArxivToCSV(csv_filename)
    csv_saver.save_to_csv(papers, append_mode=True)

    # 显示统计信息
    stats = csv_saver.get_statistics()
    print(f"\n📊 统计信息:")
    print(f"   总论文数: {stats['total_papers']}")
    print(f"   主要类别: {dict(list(stats.get('categories', {}).items())[:5])}")

if __name__ == "__main__":
    # 示例使用
    fetch_and_save_papers(
        categories=["cs.CV", "cs.AI", "cs.LG"],
        max_results=10,
        csv_filename="arxiv_papers.csv"
    )

    # 搜索示例
    print("\n🔍 搜索示例:")
    csv_saver = ArxivToCSV("arxiv_papers.csv")
    search_results = csv_saver.search_in_csv("transformer")

    if search_results:
        for i, paper in enumerate(search_results[:3], 1):
            print(f"{i}. {paper['title'][:80]}...")
            print(f"   作者: {paper['authors'][0]} 等" if paper['authors'] else "   作者: 未知")
            print(f"   类别: {', '.join(paper['categories'][:3])}")
            print()