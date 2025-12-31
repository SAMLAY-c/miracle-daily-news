#!/usr/bin/env python3
"""
Arxiv 抓取脚本测试版本
用于验证连接和功能
"""

import requests
import xml.etree.ElementTree as ET
import json
import time

# 配置
API_KEY = "t-g104c303A6373MHT63OJMF6KSKG4SWVPZU4D47NU"
APP_TOKEN = "DdCZbBA7baN2SjsUt5McCnrnnsc"
TABLE_ID = "tblb9sbMaoghEbWW"

def test_arxiv_connection():
    """测试Arxiv API连接"""
    print("🔗 测试Arxiv API连接...")

    url = "http://export.arxiv.org/api/query?search_query=cat:cs.CV&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print("✅ Arxiv API连接成功")
        return response.text
    except Exception as e:
        print(f"❌ Arxiv API连接失败: {e}")
        return None

def parse_simple_xml(xml_data):
    """简化版XML解析"""
    try:
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}

        papers = []
        for entry in root.findall('atom:entry', ns):
            # 只获取基本字段
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            arxiv_id = entry.find('atom:id', ns).text.split('/')[-1]
            summary = entry.find('atom:summary', ns).text.strip()[:200] + "..."  # 截断摘要

            # 作者（最多3个）
            authors = []
            for author in entry.findall('atom:author', ns):
                authors.append(author.find('atom:name', ns).text)
                if len(authors) >= 3:
                    break

            # 日期（简化处理）
            published = entry.find('atom:published', ns).text[:10]
            published_timestamp = int(time.time()) * 1000  # 简化为当前时间

            paper = {
                'title': title,
                'arxiv_id': arxiv_id,
                'summary': summary,
                'authors': ", ".join(authors),
                'published': published_timestamp,
                'research_field': 'CV (计算机视觉)',  # 固定为CV进行测试
                'paper_url': f"https://arxiv.org/abs/{arxiv_id}"
            }
            papers.append(paper)

        print(f"✅ 成功解析 {len(papers)} 篇论文")
        return papers

    except Exception as e:
        print(f"❌ XML解析失败: {e}")
        return []

def create_feishu_record(paper):
    """创建单条飞书记录"""
    return {
        "fields": {
            "论文标题": paper['title'],
            "摘要": paper['summary'],
            "作者": paper['authors'],
            "Arxiv ID": paper['arxiv_id'],
            "发布时间": paper['published'],
            "更新时间": paper['published'],  # 使用发布时间作为更新时间
            "研究领域": paper['research_field'],
            "学习状态": "待读",
            "原文链接": {
                "text": "Arxiv Link",
                "link": paper['paper_url']
            },
            "DOI": "",
            "期刊引用": "",
            "学习笔记": ""
        }
    }

def test_feishu_write():
    """测试写入飞书表格"""
    print("📝 测试写入飞书表格...")

    # 1. 测试Arxiv连接
    xml_data = test_arxiv_connection()
    if not xml_data:
        return False

    # 2. 解析数据
    papers = parse_simple_xml(xml_data)
    if not papers:
        return False

    # 3. 创建飞书记录（只测试前2篇）
    records = []
    for paper in papers[:2]:  # 只测试前2篇
        record = create_feishu_record(paper)
        records.append(record)

    # 4. 写入飞书
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/batch_create"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json; charset=utf-8"
    }

    payload = {"records": records}

    try:
        print(f"🚀 正在写入 {len(records)} 条测试记录...")
        response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))

        print(f"📊 HTTP状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                records_created = len(result.get('data', {}).get('records', []))
                print(f"✅ 成功写入 {records_created} 条记录")
                return True
            else:
                print(f"❌ API返回错误: {result}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 写入飞书失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始Arxiv+飞书集成测试")
    print("=" * 50)

    success = test_feishu_write()

    print("=" * 50)
    if success:
        print("🎉 测试成功！系统工作正常")
        print("💡 现在可以运行完整的 arxiv_feishu_fetcher.py 脚本")
    else:
        print("⚠️ 测试失败，请检查网络连接和API配置")

if __name__ == "__main__":
    main()