#!/usr/bin/env python3
"""
Arxiv 论文自动抓取脚本
版本: 1.0
功能: 定期从Arxiv抓取最新AI论文并自动写入飞书多维表格
"""

import requests
import xml.etree.ElementTree as ET
import json
import time
import os
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arxiv_fetcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ArxivFetcher:
    def __init__(self):
        # 飞书 API 配置
        self.APP_TOKEN = "DdCZbBA7baN2SjsUt5McCnrnnsc"
        self.TABLE_ID = "tblb9sbMaoghEbWW"
        self.API_KEY = "t-g104c303A6373MHT63OJMF6KSKG4SWVPZU4D47NU"

        # Arxiv API 配置
        self.ARXIV_BASE_URL = "http://export.arxiv.org/api/query"
        self.RATE_LIMIT = 1  # 每秒最多1次请求

        # AI 领域查询配置
        self.AI_CATEGORIES = {
            'cs.CV': 'CV (计算机视觉)',
            'cs.CL': 'NLP (自然语言处理)',
            'cs.LG': 'LLM (大语言模型)',
            'cs.AI': 'LLM (大语言模型)',
            'cs.RO': 'RL (强化学习)',
            'cs.IR': 'NLP (自然语言处理)',  # Information Retrieval
            'cs.NE': 'LLM (大语言模型)',   # Neural and Evolutionary Computing
            'cs.MM': 'Multimodal (多模态)', # Multimedia
            'default': 'Multimodal (多模态)'
        }

        # 本地存储文件
        self.PROCESSED_IDS_FILE = "processed_arxiv_ids.txt"
        self.LAST_FETCH_FILE = "last_fetch_time.txt"

    def load_processed_ids(self):
        """加载已处理的Arxiv ID集合"""
        try:
            if os.path.exists(self.PROCESSED_IDS_FILE):
                with open(self.PROCESSED_IDS_FILE, 'r') as f:
                    return set(line.strip() for line in f if line.strip())
            return set()
        except Exception as e:
            logger.error(f"加载已处理ID失败: {e}")
            return set()

    def save_processed_ids(self, ids):
        """保存已处理的Arxiv ID集合"""
        try:
            with open(self.PROCESSED_IDS_FILE, 'w') as f:
                for arxiv_id in ids:
                    f.write(f"{arxiv_id}\n")
        except Exception as e:
            logger.error(f"保存已处理ID失败: {e}")

    def add_processed_ids(self, new_ids):
        """添加新处理的ID到集合中"""
        existing_ids = self.load_processed_ids()
        updated_ids = existing_ids.union(new_ids)
        self.save_processed_ids(updated_ids)
        return updated_ids

    def get_last_fetch_time(self):
        """获取上次抓取时间"""
        try:
            if os.path.exists(self.LAST_FETCH_FILE):
                with open(self.LAST_FETCH_FILE, 'r') as f:
                    timestamp = f.read().strip()
                    return datetime.fromisoformat(timestamp)
            return datetime.now() - timedelta(days=1)  # 默认获取一天内的
        except Exception as e:
            logger.error(f"获取上次抓取时间失败: {e}")
            return datetime.now() - timedelta(days=1)

    def save_last_fetch_time(self):
        """保存本次抓取时间"""
        try:
            with open(self.LAST_FETCH_FILE, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception as e:
            logger.error(f"保存抓取时间失败: {e}")

    def fetch_arxiv_papers(self, category=None, max_results=20, days_back=1):
        """从Arxiv获取论文数据"""
        try:
            # 构建查询参数
            if category:
                search_query = f"cat:{category}"
            else:
                # 查询所有AI相关类别
                categories = list(self.AI_CATEGORIES.keys())
                search_query = " OR ".join([f"cat:{cat}" for cat in categories if cat != 'default'])

            # 设置时间范围（最近几天）
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d%H%M%S")

            params = {
                'search_query': search_query,
                'start': 0,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }

            logger.info(f"正在抓取Arxiv数据: {self.ARXIV_BASE_URL}?{params}")

            response = requests.get(self.ARXIV_BASE_URL, params=params, timeout=30)
            response.raise_for_status()

            return response.text

        except Exception as e:
            logger.error(f"抓取Arxiv数据失败: {e}")
            return None

    def parse_arxiv_xml(self, xml_data):
        """解析Arxiv XML数据"""
        try:
            root = ET.fromstring(xml_data)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}

            papers = []
            for entry in root.findall('atom:entry', ns):
                # 获取基础信息
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                summary = entry.find('atom:summary', ns).text.strip()
                paper_url = entry.find('atom:id', ns).text
                arxiv_id = paper_url.split('/')[-1]
                published = entry.find('atom:published', ns).text[:19]  # yyyy-MM-ddTHH:mm:ss
                updated = entry.find('atom:updated', ns).text[:19]

                # 处理作者
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns).text
                    authors.append(name)
                authors_str = ", ".join(authors[:10])  # 最多显示前10个作者

                # 获取PDF链接
                pdf_link = ""
                for link in entry.findall('atom:link', ns):
                    if link.attrib.get('title') == 'pdf':
                        pdf_link = link.attrib['href']
                        break

                # 处理分类
                primary_cat = entry.find('arxiv:primary_category', ns).attrib['term']
                research_field = self.AI_CATEGORIES.get(primary_cat, self.AI_CATEGORIES['default'])

                # 获取DOI
                doi = ""
                doi_element = entry.find('arxiv:doi', ns)
                if doi_element is not None:
                    doi = doi_element.text

                # 获取期刊引用
                journal_ref = ""
                journal_element = entry.find('arxiv:journal_ref', ns)
                if journal_element is not None:
                    journal_ref = journal_element.text

                # 获取评论
                comment = ""
                comment_element = entry.find('arxiv:comment', ns)
                if comment_element is not None:
                    comment = comment_element.text

                # 转换为飞书日期格式（毫秒时间戳）
                try:
                    published_dt = datetime.strptime(published, "%Y-%m-%dT%H:%M:%S")
                    updated_dt = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%S")
                    published_timestamp = int(published_dt.timestamp()) * 1000
                    updated_timestamp = int(updated_dt.timestamp()) * 1000
                except ValueError:
                    # 如果时间格式解析失败，使用当前时间
                    current_timestamp = int(time.time()) * 1000
                    published_timestamp = current_timestamp
                    updated_timestamp = current_timestamp

                paper = {
                    'arxiv_id': arxiv_id,
                    'title': title,
                    'summary': summary,
                    'authors': authors_str,
                    'published': published_timestamp,
                    'updated': updated_timestamp,
                    'research_field': research_field,
                    'paper_url': paper_url,
                    'pdf_link': pdf_link,
                    'doi': doi,
                    'journal_ref': journal_ref,
                    'comment': comment,
                    'primary_category': primary_cat
                }

                papers.append(paper)

            logger.info(f"成功解析 {len(papers)} 篇论文")
            return papers

        except Exception as e:
            logger.error(f"解析Arxiv数据失败: {e}")
            return []

    def convert_to_feishu_format(self, papers):
        """将论文数据转换为飞书API格式"""
        records = []

        for paper in papers:
            record = {
                "fields": {
                    "论文标题": paper['title'],
                    "摘要": paper['summary'],
                    "作者": paper['authors'],
                    "Arxiv ID": paper['arxiv_id'],
                    "发布时间": paper['published'],
                    "更新时间": paper['updated'],
                    "研究领域": paper['research_field'],
                    "学习状态": "待读",
                    "原文链接": {
                        "text": "Arxiv Link",
                        "link": paper['paper_url']
                    },
                    "DOI": paper['doi'],
                    "期刊引用": paper['journal_ref'],
                    "学习笔记": ""
                }
            }
            records.append(record)

        return records

    def push_to_feishu(self, records):
        """批量推送数据到飞书表格"""
        if not records:
            logger.info("没有新数据需要推送")
            return True

        try:
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.APP_TOKEN}/tables/{self.TABLE_ID}/records/batch_create"
            headers = {
                "Authorization": f"Bearer {self.API_KEY}",
                "Content-Type": "application/json; charset=utf-8"
            }

            # 飞书API限制每次最多500条记录
            batch_size = 10  # 为了稳定性，使用较小的批次
            total_success = 0
            total_failed = 0

            for i in range(0, len(records), batch_size):
                batch_records = records[i:i + batch_size]
                payload = {"records": batch_records}

                logger.info(f"正在推送第 {i//batch_size + 1} 批次，共 {len(batch_records)} 条记录")

                response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))

                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 0:
                        batch_success = len(result.get('data', {}).get('records', []))
                        total_success += batch_success
                        logger.info(f"批次推送成功，写入 {batch_success} 条记录")
                    else:
                        logger.error(f"API返回错误: {result}")
                        total_failed += len(batch_records)
                else:
                    logger.error(f"HTTP请求失败: {response.status_code}, {response.text}")
                    total_failed += len(batch_records)

                # 速率限制：每次请求后等待1秒
                time.sleep(1)

            logger.info(f"推送完成: 成功 {total_success} 条，失败 {total_failed} 条")
            return total_failed == 0

        except Exception as e:
            logger.error(f"推送数据到飞书失败: {e}")
            return False

    def run(self, max_results=20, categories=None, days_back=1):
        """执行完整的抓取流程"""
        logger.info("开始执行Arxiv论文抓取任务")

        # 加载已处理的ID集合
        processed_ids = self.load_processed_ids()
        logger.info(f"已处理的论文数量: {len(processed_ids)}")

        # 获取新论文
        all_papers = []

        if categories:
            # 按指定分类抓取
            for category in categories:
                xml_data = self.fetch_arxiv_papers(category, max_results, days_back)
                if xml_data:
                    papers = self.parse_arxiv_xml(xml_data)
                    all_papers.extend(papers)
                time.sleep(1)  # 遵守速率限制
        else:
            # 抓取所有AI分类
            xml_data = self.fetch_arxiv_papers(None, max_results, days_back)
            if xml_data:
                papers = self.parse_arxiv_xml(xml_data)
                all_papers = papers

        # 去重：只处理未见过的新论文
        new_papers = [paper for paper in all_papers if paper['arxiv_id'] not in processed_ids]

        logger.info(f"总共获取 {len(all_papers)} 篇论文，其中新论文 {len(new_papers)} 篇")

        if new_papers:
            # 转换为飞书格式
            feishu_records = self.convert_to_feishu_format(new_papers)

            # 推送到飞书
            success = self.push_to_feishu(feishu_records)

            if success:
                # 更新已处理ID集合
                new_ids = [paper['arxiv_id'] for paper in new_papers]
                self.add_processed_ids(new_ids)
                self.save_last_fetch_time()
                logger.info(f"成功处理 {len(new_papers)} 篇新论文")
            else:
                logger.error("推送失败，不更新已处理ID集合")
        else:
            logger.info("没有新论文需要处理")

        logger.info("Arxiv论文抓取任务完成")


def main():
    """主函数"""
    fetcher = ArxivFetcher()

    # 配置参数
    max_results = 30  # 每次最多获取30篇论文
    days_back = 2     # 获取最近2天的论文

    # 可以指定特定分类，如 ['cs.CV', 'cs.CL']，或设为None获取所有分类
    categories = None  # ['cs.CV', 'cs.LG']  # 示例：只获取CV和LG分类

    # 执行抓取任务
    fetcher.run(max_results=max_results, categories=categories, days_back=days_back)


if __name__ == "__main__":
    main()