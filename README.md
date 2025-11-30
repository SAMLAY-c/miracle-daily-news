# 🚀 Hacker News 飞书自动化情报站

这是一个自动化抓取 Hacker News 热门新闻，使用 AI 进行投资视角分析，并自动写入飞书多维表格的完整解决方案。

## 📁 核心文件

- **`setup_feishu_fields.py`** - 飞书表格字段创建工具
- **`hacker_news_feishu_final.py`** - 主要的抓取、分析、写入程序
- **`.env`** - 环境变量配置文件
- **`requirements.txt`** - Python 依赖包列表

## 🎯 功能特点

- **🧠 AI 智能分析**：使用 DeepSeek-V3 模型进行投资视角分析
- **📊 结构化数据**：自动提取摘要、领域、影响、商业潜力等维度
- **🤖 自动化写入**：无需手动操作，直接写入飞书表格
- **🛡️ 容错机制**：完善的错误处理和默认值填充
- **📝 实时日志**：详细的进度显示和错误提示

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

已配置在 `.env` 文件中，包含：
- SiliconFlow API Key (DeepSeek)
- 飞书应用凭证
- 飞书多维表格信息

### 3. 运行字段创建（首次使用）

```bash
python3 setup_feishu_fields.py
```

### 4. 运行主程序

```bash
python3 hacker_news_feishu_final.py
```

## 📋 飞书表格字段

程序会在飞书多维表格中创建以下字段：

| 字段名称 | 字段类型 | 说明 |
| :--- | :--- | :--- |
| **新闻标题** | 多行文本 | Hacker News 新闻标题 |
| **发布日期** | 日期 | 新闻发布时间 |
| **原文链接** | 超链接 | 可点击访问原文 |
| **HN热度** | 数字 | Hacker News 点赞数 |
| **所属领域** | 单选 | AI 自动分类：Generative AI, SaaS, 硬科技, 开发工具, Web3, 生物科技, 其他 |
| **一句话摘要** | 多行文本 | AI 生成的摘要 |
| **底层逻辑** | 多行文本 | AI 分析的本质原因 |
| **潜在影响** | 多行文本 | AI 分析的行业影响 |
| **商业潜力** | 评分 | AI 评估的 1-5 星评分 |
| **AI推荐** | 单选 | AI 推荐指数：🔥 必读, 👀 值得关注, ☕️ 随便看看 |
| **收藏日期** | 日期 | 程序抓取时间 |

## 🎨 示例输出

```
🚀 启动自动化情报系统...
📡 正在抓取 Top 10 条新闻...
✅ 成功获取 10 条数据

🧠 正在分析: CachyOS: Fast and Customizable Linux Dis...
   💾 [写入成功] 商业潜力: 3星 | 👀 值得关注

🧠 正在分析: Show HN: Boing...
   💾 [写入成功] 商业潜力: 3星 | 👀 值得关注

🎉 任务结束！共成功写入 10 条新闻。
```

## 🛠 技术架构

- **数据源**：Hacker News Firebase API
- **AI 分析**：SiliconFlow API (DeepSeek-V3 模型)
- **存储**：飞书多维表格 API
- **语言**：Python 3.9+
- **依赖**：requests, python-dotenv, pytz, urllib3<2.0

## ⚙️ AI 分析维度

程序会从以下 6 个维度分析每条新闻：

1. **摘要 (summary)**：一句话总结新闻内容
2. **领域 (category)**：自动归类到技术领域
3. **底层逻辑 (reason)**：分析事件本质和原因
4. **潜在影响 (impact)**：评估对行业的影响
5. **商业潜力 (commercial_score)**：1-5 星评分
6. **推荐指数 (recommendation)**：必读/值得关注/随便看看

## 🔧 配置说明

### 环境变量

```ini
# SiliconFlow (DeepSeek) 配置
SILICON_KEY='sk-your-api-key'
NEWS_LIMIT=5

# 飞书开放平台配置
FEISHU_APP_ID='cli_your_app_id'
FEISHU_APP_SECRET='your_app_secret'

# 飞书多维表格配置
FEISHU_BITABLE_APP_TOKEN='your_base_token'
FEISHU_BITABLE_TABLE_ID='your_table_id'
```

### 飞书配置

1. **创建应用**：在 [飞书开发者后台](https://open.feishu.cn/app) 创建企业自建应用
2. **开通权限**：确保开通 `bitable:app` 相关权限
3. **发布应用**：创建版本并申请发布
4. **添加协作**：在多维表格中添加该应用并授予编辑权限

## 🚨 常见问题

### Q: 提示字段创建失败？
A: 检查以下项目：
- 飞书应用是否已发布并启用
- 是否已开通 `bitable:app:manager` 权限
- 是否已将应用添加到多维表格协作中

### Q: AI 分析失败？
A: 可能是 API Key 无效或网络问题，检查 `.env` 文件中的配置

### Q: 数据写入失败？
A: 确认字段名称与飞书表格中的列名完全一致（包括空格）

## 📞 技术支持

如遇到问题，请检查：
1. `.env` 文件配置是否正确
2. 飞书应用权限是否已开通
3. 飞书表格字段是否创建成功
4. 应用是否已添加到表格协作中

---

**🎉 祝你使用愉快！让 AI 为你发掘科技趋势！**