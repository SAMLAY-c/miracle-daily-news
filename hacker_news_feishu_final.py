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
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", 'cli_a9a5b41b8abf1ced')
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", 'M8azGTlTa9Aqwv19fdUZwge714CqFWD1')

# 3. 飞书多维表格配置 (根据你提供的 Base 链接填入)
FEISHU_BITABLE_APP_TOKEN = os.getenv("FEISHU_BITABLE_APP_TOKEN", 'ddCZbBA7baN2SjsUt5McCnrnnsc')
FEISHU_TABLE_ID = os.getenv("FEISHU_BITABLE_TABLE_ID", 'tblb9sbMaoghEbWW')

NEWS_LIMIT = int(os.getenv("NEWS_LIMIT", 5))
ARXIV_LIMIT = int(os.getenv("ARXIV_LIMIT", 3))
ARXIV_CATEGORIES = os.getenv("ARXIV_CATEGORIES", "cs.CV,cs.AI,cs.LG").split(",")

# ===========================================

# 提示词模板
PROMPT_TEMPLATE = """
你是一位像陆奇博士一样敏锐的风险投资人。请阅读以下科技新闻标题。
请进行深度分析，并严格按照 JSON 格式返回结果（不要返回 Markdown 代码块）。

需要分析的维度（JSON Key 必须严格一致）：
1. "summary": 一句话摘要（中文，50字内）。
2. "category": 所属领域，必须从以下选项中严格选择一个：
   ["Generative AI", "SaaS", "硬科技", "开发工具", "Web3", "生物科技", "其他"]
3. "reason": 底层逻辑。这件事为什么发生？解决了什么本质问题？（中文，50字内）。
4. "impact": 潜在影响。对行业或开发者意味着什么？（中文，50字内）。
5. "commercial_score": 商业落地潜力评分，返回整数 1 到 5（5为最高）。
6. "recommendation": 推荐指数，必须从以下选项中严格选择一个：
   ["🔥 必读", "👀 值得关注", "☕️ 随便看看"]

新闻标题：{title}
"""

# arXiv 论文专用提示词模板
ARXIV_PROMPT_TEMPLATE = """
你是一位资深的AI研究员和技术投资顾问。请分析以下 arXiv 论文信息，评估其技术价值和商业潜力。

请严格按照 JSON 格式返回结果（不要返回 Markdown 代码块）。

需要分析的维度（JSON Key 必须严格一致）：
1. "summary": 技术贡献摘要（中文，50字内）。
2. "category": 所属领域，必须从以下选项中严格选择一个：
   ["Generative AI", "计算机视觉", "自然语言处理", "机器学习", "强化学习", "其他"]
3. "innovation": 技术创新性评估，简述其核心创新点（中文，50字内）。
4. "practicality": 实用性评估，技术落地的可行性和难度（中文，50字内）。
5. "commercial_score": 商业潜力评分，返回整数 1 到 5（5为最高）。
6. "recommendation": 推荐指数，必须从以下选项中严格选择一个：
   ["🔥 重大突破", "👀 重要进展", "☕️ 学术价值"]

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

def get_hn_news(limit=NEWS_LIMIT):
    """抓取 Hacker News 热门新闻（带去重功能）"""
    print(f"📡 正在抓取 Top {limit} 条新闻...")
    try:
        # 读取已处理过的新闻标题文件
        processed_titles = set()
        processed_file = 'processed_hacker_news_titles.txt'

        if os.path.exists(processed_file):
            print(f"📖 已找到历史记录，读取 {processed_file}")
            with open(processed_file, 'r', encoding='utf-8') as f:
                processed_titles = set(line.strip() for line in f if line.strip())

        # 获取更多新闻以便过滤
        top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:limit * 2]  # 获取更多以过滤
        stories = []
        skipped_count = 0
        processed_count = 0

        for tid in top_ids:
            if len(stories) >= limit:  # 已达到目标数量
                break

            try:
                item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{tid}.json").json()
                if item and item.get('url') and item.get('title'):
                    title = item.get('title', '').strip()
                    # 检查是否已处理过
                    if title not in processed_titles:
                        stories.append(item)
                        # 实时添加到已处理列表
                        processed_titles.add(title)
                    else:
                        skipped_count += 1
                        processed_count += 1
            except Exception as e:
                print(f"⚠️ 获取新闻 {tid} 时出错: {e}")
                continue

        # 保存新处理的标题到文件
        if stories:
            new_titles = [item.get('title', '').strip() for item in stories]
            print(f"💾 保存 {len(new_titles)} 个新标题到历史记录")
            with open(processed_file, 'w', encoding='utf-8') as f:
                for title in sorted(processed_titles.union(new_titles)):
                    f.write(f"{title}\n")

        print(f"✅ 成功获取 {len(stories)} 条新数据（跳过 {processed_count} 条重复）")

        return stories[:limit]  # 确保返回正确的数量
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return []

def get_arxiv_papers(limit=ARXIV_LIMIT, categories=ARXIV_CATEGORIES):
    """获取最新 arXiv 论文（带去重功能）"""
    print(f"📚 正在获取 arXiv 最新论文...")
    try:
        fetcher = ArxivFetcher(delay_seconds=2)  # 2秒间隔，遵守速率限制
        papers = fetcher.fetch_latest_papers(
            categories=categories,
            max_results=limit
        )

        # 为每个论文添加来源标识
        for paper in papers:
            paper['source'] = 'arxiv'

        return papers

    except Exception as e:
        print(f"❌ 获取 arXiv 论文失败: {e}")
        return []

def analyze_and_write(news_items, token):
    """AI 分析并写入飞书"""
    # 飞书写入接口
    feishu_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BITABLE_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records/batch_create"
    feishu_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # DeepSeek 接口
    ai_url = "https://api.siliconflow.cn/v1/chat/completions"
    ai_headers = {"Authorization": f"Bearer {SILICON_KEY}", "Content-Type": "application/json"}

    success_count = 0
    failed_count = 0
    records = []

    for item in news_items:
        title = item.get('title', '无标题')
        source = item.get('source', 'unknown')
        print(f"\n🧠 正在分析: {title[:40]}...")

        try:
            # 选择正确的提示词模板
            if source == 'arxiv':
                # arXiv 论文专用模板
                prompt = ARXIV_PROMPT_TEMPLATE.format(
                    title=title,
                    summary=item.get('summary', '')[:200],
                    authors=', '.join(item.get('authors', [])[:3]),
                    categories=', '.join(item.get('categories', [])[:3])
                )
            else:
                # Hacker News 通用模板
                prompt = PROMPT_TEMPLATE.format(title=title)

            # 调用 AI
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
            }

            ai_resp = requests.post(ai_url, headers=ai_headers, json=payload)
            ai_data = ai_resp.json()

            # 解析 AI 返回的内容
            content_str = ai_data['choices'][0]['message']['content']
            analysis = json.loads(content_str)

            # 构造飞书数据 Payload (使用正确的字段ID)
            current_time_ms = int(time.time() * 1000)

            fields = {
                "fldRJ6ZXT2": current_time_ms,  # 收藏日期
                "fldQySf922": title,  # 新闻标题/论文标题
                "fldhcSKytX": int(time.time() * 1000),  # 发布日期
                "fld0fcfgz0": item.get('id') or item.get('url'),  # 原文链接
                "fld7j1isdW": item.get('score', 0) if source != 'arxiv' else 0,  # HN热度 (arXiv设为0)
                "fldkkjQi8y": analysis.get('category', '其他'),  # 所属领域
                "fldom51JuS": analysis.get('summary', '分析失败'),  # 一句话摘要
                "fld0RXbCrS": analysis.get('reason', analysis.get('innovation', '')),  # 底层逻辑/技术创新性
                "fld0vyHCr2": analysis.get('impact', analysis.get('practicality', '')),  # 潜在影响/实用性评估
                "fldwYrkaCR": analysis.get('recommendation', '☕️ 随便看看'),  # AI推荐
                "fldhwToUil": analysis.get('commercial_score', 3)  # 商业潜力
            }

            records.append({"fields": fields})

            print(f"   ✅ [分析完成] 商业潜力: {analysis.get('commercial_score')}星 | {analysis.get('recommendation')}")
            success_count += 1

        except Exception as e:
            print(f"   ❌ 处理出错: {e}")
            failed_count += 1

        # 避免请求过快
        time.sleep(1)

    # 批量写入飞书
    if records:
        try:
            write_payload = {"records": records}
            write_resp = requests.post(feishu_url, headers=feishu_headers, json=write_payload)
            write_res = write_resp.json()

            if write_res.get('code') == 0:
                print(f"\n💾 [批量写入成功] 成功写入 {len(records)} 条记录")
            else:
                print(f"\n❌ [批量写入失败] {write_res.get('msg')}")
                if 'data' in write_res and write_res['data']:
                    print("错误详情:", write_res['data'])
        except Exception as e:
            print(f"\n❌ 批量写入出错: {e}")

    print(f"\n🎉 任务结束！")
    print(f"   ✅ 成功分析: {success_count} 条新闻")
    print(f"   ❌ 失败: {failed_count} 条新闻")
    print(f"   📊 处理效率: {success_count}/{len(news_items)}")

def show_processed_history():
    """显示已处理的历史记录"""
    processed_file = 'processed_hacker_news_titles.txt'
    if os.path.exists(processed_file):
        print(f"📖 {processed_file} 中的已处理标题:")
        print("=" * 50)
        with open(processed_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if line.strip():
                    print(f"{i:3d}. {line.strip()}")
        print("=" * 50)
    else:
        print(f"📖 {processed_file} 不存在，这是首次运行")

if __name__ == "__main__":
    print("🚀 Hacker News + arXiv 论文飞书自动化情报站 (去重版)")
    print("=" * 60)

    # 显示历史记录
    show_processed_history()
    print()

    # 1. 获取 Token
    t_token = get_tenant_token()

    if t_token:
        # 2. 获取 Hacker News 新闻（带去重）
        print("📰 获取 Hacker News...")
        hn_list = get_hn_news(limit=NEWS_LIMIT)

        # 3. 获取 arXiv 论文（带去重）
        print("📚 获取 arXiv 论文...")
        arxiv_list = get_arxiv_papers(limit=ARXIV_LIMIT, categories=ARXIV_CATEGORIES)

        # 合并数据
        all_items = []
        if hn_list:
            for item in hn_list:
                item['source'] = 'hacker_news'
                all_items.append(item)

        if arxiv_list:
            all_items.extend(arxiv_list)

        if all_items:
            print(f"\n📊 数据统计:")
            print(f"   Hacker News: {len(hn_list)} 条")
            print(f"   arXiv 论文: {len(arxiv_list)} 条")
            print(f"   总计: {len(all_items)} 条")
            print()

            # 4. 分析 + 写入
            analyze_and_write(all_items, t_token)
        else:
            print("⚠️ 未获取到任何数据")
    else:
        print("⚠️ 无法连接飞书，请检查 App ID 和 Secret")