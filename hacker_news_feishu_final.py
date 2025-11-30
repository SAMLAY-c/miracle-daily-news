import requests
import json
import time
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ================= 配置区域 =================

# 1. SiliconFlow (DeepSeek) 配置
SILICON_KEY = os.getenv("SILICON_KEY", 'sk-keakcptlwtptnosbliohqompvsgxdtwctolxqjiwxddahyqk')
MODEL_NAME = "deepseek-ai/DeepSeek-V3"

# 2. 飞书机器人配置
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", 'cli_a9a694741d38dbd7')
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", 'UenXmsnXoKjyQVh5arXtBcyAoneKudgI')

# 3. 飞书多维表格配置 (根据你提供的 Base 链接填入)
FEISHU_BITABLE_APP_TOKEN = os.getenv("FEISHU_BITABLE_APP_TOKEN", 'Cprlb3kZFaBOyNsleepcdSAJnN5')
FEISHU_TABLE_ID = os.getenv("FEISHU_BITABLE_TABLE_ID", 'tblS7Lr8KRKHYBDo')

NEWS_LIMIT = int(os.getenv("NEWS_LIMIT", 5))

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
    """抓取 Hacker News 热门新闻"""
    print(f"📡 正在抓取 Top {limit} 条新闻...")
    try:
        # 获取 Top Stories ID 列表
        top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:limit]
        stories = []
        for tid in top_ids:
            # 获取单条详情
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{tid}.json").json()
            if item and item.get('url'):  # 只保留有链接的新闻
                stories.append(item)
        print(f"✅ 成功获取 {len(stories)} 条数据")
        return stories
    except Exception as e:
        print(f"❌ 抓取 HN 失败: {e}")
        return []

def analyze_and_write(news_items, token):
    """AI 分析并写入飞书"""
    # 飞书写入接口
    feishu_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BITABLE_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
    feishu_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # DeepSeek 接口
    ai_url = "https://api.siliconflow.cn/v1/chat/completions"
    ai_headers = {"Authorization": f"Bearer {SILICON_KEY}", "Content-Type": "application/json"}

    success_count = 0

    for item in news_items:
        title = item.get('title', '无标题')
        print(f"\n🧠 正在分析: {title[:40]}...")

        # 1. 调用 AI
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": PROMPT_TEMPLATE.format(title=title)}],
            "response_format": {"type": "json_object"},  # 强制 JSON
            "temperature": 0.3
        }

        try:
            ai_resp = requests.post(ai_url, headers=ai_headers, json=payload)
            ai_data = ai_resp.json()

            # 解析 AI 返回的内容
            content_str = ai_data['choices'][0]['message']['content']
            analysis = json.loads(content_str)

            # 2. 构造飞书数据 Payload (字段名必须与表格完全一致)
            current_time_ms = int(time.time() * 1000)  # 当前时间戳

            fields = {
                "新闻标题": title,
                "一句话摘要": analysis.get('summary', '分析失败'),
                "所属领域": analysis.get('category', '其他'),  # 单选
                "底层逻辑": analysis.get('reason', ''),
                "潜在影响": analysis.get('impact', ''),
                "商业潜力": analysis.get('commercial_score', 3),  # 评分(1-5)
                "AI推荐": analysis.get('recommendation', '☕️ 随便看看'),  # 单选
                "HN热度": item.get('score', 0),
                "发布日期": int(item.get('time', time.time()) * 1000),  # HN发布时间
                "收藏日期": current_time_ms,  # ✅ 这里是你新加的字段，填入当前时间
                "原文链接": {
                    "text": "点击阅读原文",
                    "link": item.get('url')
                }
            }

            # 3. 写入飞书
            write_resp = requests.post(feishu_url, headers=feishu_headers, json={"fields": fields})
            write_res = write_resp.json()

            if write_res.get('code') == 0:
                print(f"   💾 [写入成功] 商业潜力: {analysis.get('commercial_score')}星 | {analysis.get('recommendation')}")
                success_count += 1
            else:
                print(f"   ❌ [写入失败] {write_res.get('msg')}")
                # 调试用：如果失败打印 payload 看格式对不对
                # print(json.dumps(fields, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"   ❌ 处理出错: {e}")

        # 避免请求过快
        time.sleep(1)

    print(f"\n🎉 任务结束！共成功写入 {success_count} 条新闻。")

if __name__ == "__main__":
    print("🚀 启动自动化情报系统...")

    # 1. 拿 Token
    t_token = get_tenant_token()

    if t_token:
        # 2. 爬新闻
        news_list = get_hn_news(limit=NEWS_LIMIT)  # 默认抓5条，可修改

        if news_list:
            # 3. 分析 + 写入
            analyze_and_write(news_list, t_token)
        else:
            print("⚠️ 未获取到新闻数据")
    else:
        print("⚠️ 无法连接飞书，请检查 App ID 和 Secret")