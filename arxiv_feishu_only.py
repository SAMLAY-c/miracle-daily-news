#!/usr/bin/env python3
"""
只处理 arXiv 论文并写入飞书多维表格的程序
"""

import requests
import json
import time
import os
from dotenv import load_dotenv
from arxiv_fetcher import ArxivFetcher

# 加载环境变量
load_dotenv()

# ================= 配置区域 =================

# 1. SiliconFlow (DeepSeek) 配置
SILICON_KEY = os.getenv("SILICON_KEY", 'sk-keakcptlwtptnosbliohqompvsgxdtwctolxqjiwxddahyqk')
MODEL_NAME = "deepseek-ai/DeepSeek-V3"

# 2. 飞书机器人配置
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", 'cli_a9db5c1e15795bc0')
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", 'OBeaUaz1mtuQPPLuhgO5kfKCaPluKBVI')

# 3. 飞书多维表格配置
FEISHU_BITABLE_APP_TOKEN = os.getenv("FEISHU_BITABLE_APP_TOKEN", 'ECRabFuuRaGRBvsgo4scULlSn1d')
FEISHU_TABLE_ID = os.getenv("FEISHU_BITABLE_TABLE_ID", 'tblMKVkH5tc2pnTK')

# arXiv 配置
ARXIV_LIMIT = int(os.getenv("ARXIV_LIMIT", 10))  # 每次获取10篇论文
ARXIV_CATEGORIES = os.getenv("ARXIV_CATEGORIES", "cs.CL,cs.AI,cs.LG,cs.CV").split(",")  # LLM相关类别：CL(计算语言学), AI, LG(机器学习), CV(计算机视觉-多模态)

# ===========================================

# arXiv 论文专用提示词模板（专注LLM分析）
ARXIV_PROMPT_TEMPLATE = """
你是一位资深的AI研究员和LLM技术专家，专注于大语言模型领域。请分析以下 arXiv 论文信息，重点评估其在LLM领域的技术价值和商业潜力。

请严格按照 JSON 格式返回结果（不要返回 Markdown 代码块）。

需要分析的维度（JSON Key 必须严格一致）：
1. "summary": 技术贡献摘要（中文，60字内）。
2. "category": 所属领域，必须从以下选项中严格选择一个：
   ["大语言模型", "模型架构", "训练优化", "推理加速", "多模态", "Agent系统", "RAG检索增强", "模型评估", "数据集", "其他"]
3. "innovation": 技术创新性评估，简述其核心创新点和对LLM领域的贡献（中文，80字内）。
4. "practicality": 实用性评估，技术落地的可行性和难度（中文，80字内）。
5. "commercial_score": 商业落地潜力评分，返回整数 1 到 5（5为最高）。
6. "recommendation": 推荐指数，必须从以下选项中严格选择一个：
   ["🔥 必读论文", "👀 重要进展", "☕️ 学术参考", "📄 方法论贡献"]

论文标题：{title}
论文摘要：{summary}
作者：{authors}
类别：{categories}
"""

def get_tenant_token():
    """获取飞书机器人访问凭证"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    try:
        resp = requests.post(url, json=payload)
        if resp.status_code != 200:
            print(f"❌ 机器人 Token 获取失败: {resp.text}")
            return None
        return resp.json().get("tenant_access_token")
    except Exception as e:
        print(f"❌ 网络请求错误: {e}")
        return None

def get_arxiv_papers(limit=ARXIV_LIMIT, categories=ARXIV_CATEGORIES):
    """获取最新 arXiv 论文（带去重功能）"""
    print(f"📚 正在获取 arXiv 最新论文...")
    print(f"   类别: {', '.join(categories)}")
    print(f"   数量: {limit}")

    try:
        fetcher = ArxivFetcher(delay_seconds=2)  # 2秒间隔，遵守速率限制
        papers = fetcher.fetch_latest_papers(
            categories=categories,
            max_results=limit
        )

        # 为每个论文添加来源标识
        for paper in papers:
            paper['source'] = 'arxiv'

        print(f"✅ 成功获取 {len(papers)} 篇新论文")
        return papers

    except Exception as e:
        print(f"❌ 获取 arXiv 论文失败: {e}")
        return []

def analyze_and_write(arxiv_papers, token):
    """AI 分析 arXiv 论文并写入飞书"""
    # 飞书写入接口（使用单条记录接口）
    feishu_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BITABLE_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
    feishu_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # DeepSeek 接口
    ai_url = "https://api.siliconflow.cn/v1/chat/completions"
    ai_headers = {"Authorization": f"Bearer {SILICON_KEY}", "Content-Type": "application/json"}

    success_count = 0
    failed_count = 0

    for paper in arxiv_papers:
        title = paper.get('title', '无标题')
        print(f"\n🧠 正在分析: {title[:50]}...")

        try:
            # 1. 调用 AI 分析
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": ARXIV_PROMPT_TEMPLATE.format(
                    title=title,
                    summary=paper.get('summary', '')[:200],
                    authors=', '.join(paper.get('authors', [])[:3]),
                    categories=', '.join(paper.get('categories', [])[:3])
                )}],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
            }

            ai_resp = requests.post(ai_url, headers=ai_headers, json=payload)
            ai_data = ai_resp.json()

            # 解析 AI 返回的内容
            content_str = ai_data['choices'][0]['message']['content']
            analysis = json.loads(content_str)

            # 2. 构造飞书数据 Payload（使用字段名称）
            current_time_ms = int(time.time() * 1000)

            fields = {
                "论文标题": title,
                "一句话摘要": analysis.get('summary', '分析失败'),
                "所属领域": analysis.get('category', '其他'),
                "技术创新性": analysis.get('innovation', ''),
                "实用性评估": analysis.get('practicality', ''),
                "商业潜力": analysis.get('commercial_score', 3),
                "AI推荐": analysis.get('recommendation', '☕️ 学术价值'),
                "发布日期": current_time_ms,
                "收藏日期": current_time_ms,
                "原文链接": {
                    "text": "Arxiv Link",
                    "link": paper.get('id', '')
                }
            }

            # 3. 逐条写入飞书
            write_resp = requests.post(feishu_url, headers=feishu_headers, json={"fields": fields})
            write_res = write_resp.json()

            if write_res.get('code') == 0:
                print(f"   💾 [写入成功] 商业潜力: {analysis.get('commercial_score')}星 | {analysis.get('recommendation')}")
                success_count += 1
            else:
                print(f"   ❌ [写入失败] {write_res.get('msg')}")
                if 'error' in write_res:
                    print(f"      详情: {write_res['error'].get('message')}")
                failed_count += 1

        except Exception as e:
            print(f"   ❌ 处理出错: {e}")
            failed_count += 1

        # 避免请求过快
        time.sleep(1)

    print(f"\n🎉 arXiv 处理任务结束！")
    print(f"   ✅ 成功分析并写入: {success_count} 篇论文")
    print(f"   ❌ 失败: {failed_count} 篇论文")
    print(f"   📊 处理效率: {success_count}/{len(arxiv_papers)}")
    print(f"   📊 飞书表格链接: https://pcnlp18cy9bm.feishu.cn/base/{FEISHU_BITABLE_APP_TOKEN}?table={FEISHU_TABLE_ID}")

if __name__ == "__main__":
    print("🚀 arXiv 论文飞书自动化情报站")
    print("=" * 50)

    # 1. 获取 Token
    t_token = get_tenant_token()

    if t_token:
        # 2. 获取 arXiv 论文（带去重）
        arxiv_list = get_arxiv_papers(limit=ARXIV_LIMIT, categories=ARXIV_CATEGORIES)

        if arxiv_list:
            # 3. 分析 + 写入
            analyze_and_write(arxiv_list, t_token)
        else:
            print("⚠️ 未获取到论文数据")
    else:
        print("⚠️ 无法连接飞书，请检查 App ID 和 Secret")