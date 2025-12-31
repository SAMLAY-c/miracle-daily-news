import requests
import xml.etree.ElementTree as ET
import time
import os
import re
from typing import List, Dict, Optional, Set

class ArxivFetcher:
    """arXiv API 查询模块，支持论文获取和去重"""

    def __init__(self, delay_seconds: int = 1):
        """
        初始化 arXiv 获取器

        Args:
            delay_seconds: 请求间隔时间，遵守 arXiv 1秒1次的限制
        """
        self.base_url = "http://export.arxiv.org/api/query"
        self.delay_seconds = delay_seconds
        self.namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        self.processed_file = 'processed_arxiv_ids.txt'

    def _make_request(self, params: Dict) -> str:
        """发起 API 请求，包含速率限制"""
        time.sleep(self.delay_seconds)  # 遵守速率限制

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"API 请求失败: {e}")

    def _parse_arxiv_id(self, arxiv_url: str) -> str:
        """从 arXiv URL 提取论文 ID"""
        # 匹配格式: http://arxiv.org/abs/2301.xxxxx 或 https://arxiv.org/abs/2301.xxxxx
        match = re.search(r'arxiv\.org/abs/(\d+\.\d+)', arxiv_url)
        return match.group(1) if match else arxiv_url

    def _load_processed_ids(self) -> Set[str]:
        """加载已处理的论文 ID"""
        if not os.path.exists(self.processed_file):
            return set()

        try:
            with open(self.processed_file, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        except Exception as e:
            print(f"⚠️ 读取已处理 ID 文件失败: {e}")
            return set()

    def _save_processed_ids(self, processed_ids: Set[str]) -> None:
        """保存已处理的论文 ID"""
        try:
            with open(self.processed_file, 'w', encoding='utf-8') as f:
                for paper_id in sorted(processed_ids):
                    f.write(f"{paper_id}\n")
        except Exception as e:
            print(f"⚠️ 保存已处理 ID 文件失败: {e}")

    def fetch_latest_papers(self,
                          categories: List[str] = ["cs.CV", "cs.AI", "cs.LG"],
                          max_results: int = 20,
                          days_back: int = 1) -> List[Dict]:
        """
        获取最新的 arXiv 论文（带去重功能）

        Args:
            categories: 论文类别列表，如 ["cs.CV", "cs.AI"]
            max_results: 最大获取数量
            days_back: 查询最近几天的论文

        Returns:
            论文信息列表
        """
        print(f"📡 正在获取 arXiv 最新论文...")
        print(f"   类别: {', '.join(categories)}")
        print(f"   数量: {max_results}")

        # 构建查询语句
        category_query = " OR ".join([f"cat:{cat}" for cat in categories])

        params = {
            'search_query': category_query,
            'start': 0,
            'max_results': max_results * 2,  # 获取更多以便过滤
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }

        try:
            # 加载已处理的论文 ID
            processed_ids = self._load_processed_ids()
            print(f"📖 已找到 {len(processed_ids)} 个历史论文记录")

            # 发起请求
            xml_data = self._make_request(params)
            root = ET.fromstring(xml_data)

            papers = []
            new_papers_count = 0
            skipped_count = 0

            for entry in root.findall('atom:entry', self.namespace):
                if len(papers) >= max_results:
                    break

                try:
                    # 解析论文信息
                    paper_info = self._parse_paper_entry(entry)
                    paper_id = self._parse_arxiv_id(paper_info['id'])

                    # 检查是否已处理过
                    if paper_id in processed_ids:
                        skipped_count += 1
                        continue

                    # 添加论文 ID 到已处理集合
                    paper_info['arxiv_id'] = paper_id
                    papers.append(paper_info)
                    processed_ids.add(paper_id)
                    new_papers_count += 1

                except Exception as e:
                    print(f"⚠️ 解析论文条目时出错: {e}")
                    continue

            # 保存更新后的已处理 ID 列表
            if new_papers_count > 0:
                self._save_processed_ids(processed_ids)
                print(f"💾 已保存 {new_papers_count} 个新论文 ID")

            print(f"✅ 成功获取 {len(papers)} 篇新论文（跳过 {skipped_count} 篇重复）")
            return papers

        except Exception as e:
            print(f"❌ 获取 arXiv 论文失败: {e}")
            return []

    def _parse_paper_entry(self, entry) -> Dict:
        """解析单个论文条目"""
        # 基本信息
        paper_id = entry.find('atom:id', self.namespace).text
        title = entry.find('atom:title', self.namespace).text.strip()
        summary = entry.find('atom:summary', self.namespace).text.strip()

        # 作者信息
        authors = []
        for author in entry.findall('atom:author', self.namespace):
            name = author.find('atom:name', self.namespace).text.strip()
            authors.append(name)

        # 时间信息
        published = entry.find('atom:published', self.namespace).text
        updated = entry.find('atom:updated', self.namespace).text

        # 链接信息
        pdf_url = None
        for link in entry.findall('atom:link', self.namespace):
            if link.get('title') == 'pdf':
                pdf_url = link.get('href')
                break

        # 提取类别信息
        categories = []
        for category in entry.findall('atom:category', self.namespace):
            term = category.get('term')
            if term:
                categories.append(term)

        return {
            'id': paper_id,
            'title': title,
            'summary': summary,
            'authors': authors,
            'published': published,
            'updated': updated,
            'pdf_url': pdf_url,
            'categories': categories,
            'source': 'arxiv'
        }

    def search_papers(self,
                     query: str,
                     max_results: int = 10,
                     sort_by: str = "relevance") -> List[Dict]:
        """
        搜索特定主题的论文

        Args:
            query: 搜索关键词，如 "transformer attention"
            max_results: 最大返回数量
            sort_by: 排序方式: "relevance", "lastUpdatedDate", "submittedDate"

        Returns:
            论文信息列表
        """
        print(f"🔍 正在搜索 arXiv 论文: {query}")

        params = {
            'search_query': f'all:"{query}"',
            'start': 0,
            'max_results': max_results,
            'sortBy': sort_by,
            'sortOrder': 'descending'
        }

        try:
            xml_data = self._make_request(params)
            root = ET.fromstring(xml_data)

            papers = []
            for entry in root.findall('atom:entry', self.namespace):
                if len(papers) >= max_results:
                    break

                try:
                    paper_info = self._parse_paper_entry(entry)
                    papers.append(paper_info)
                except Exception as e:
                    print(f"⚠️ 解析论文条目时出错: {e}")
                    continue

            print(f"✅ 搜索完成，找到 {len(papers)} 篇相关论文")
            return papers

        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []

    def get_paper_by_id(self, paper_id: str) -> Optional[Dict]:
        """根据论文 ID 获取详细信息"""
        params = {
            'search_query': f'id:{paper_id}',
            'start': 0,
            'max_results': 1
        }

        try:
            xml_data = self._make_request(params)
            root = ET.fromstring(xml_data)

            entries = root.findall('atom:entry', self.namespace)
            if entries:
                paper_info = self._parse_paper_entry(entries[0])
                paper_info['arxiv_id'] = paper_id
                return paper_info

            return None

        except Exception as e:
            print(f"❌ 获取论文 {paper_id} 失败: {e}")
            return None

# 示例使用
if __name__ == "__main__":
    # 创建获取器
    fetcher = ArxivFetcher(delay_seconds=2)  # 2秒间隔，保守起见

    # 获取最新论文
    latest_papers = fetcher.fetch_latest_papers(
        categories=["cs.CV", "cs.AI"],
        max_results=5
    )

    print(f"\n📚 最新论文:")
    for paper in latest_papers:
        print(f"   标题: {paper['title'][:80]}...")
        print(f"   作者: {', '.join(paper['authors'][:3])}{'等' if len(paper['authors']) > 3 else ''}")
        print(f"   类别: {', '.join(paper['categories'][:3])}")
        print(f"   链接: {paper['id']}")
        print()