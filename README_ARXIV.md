# arXiv 论文自动获取和本地存储工具

基于你提供的 arXiv API 信息，这个工具可以自动获取最新论文并保存到本地 CSV 文件，支持去重、搜索和导出功能。

## 🚀 功能特点

- **自动获取**: 定期从 arXiv API 获取最新论文
- **去重机制**: 避免重复处理相同的论文
- **本地存储**: 将论文信息保存为 CSV 格式
- **搜索功能**: 在本地数据中搜索关键词
- **统计分析**: 查看论文类别、年份分布等统计信息
- **导出功能**: 导出为 Markdown 格式，便于阅读和分享
- **速率控制**: 遵守 arXiv 1秒1次的访问限制

## 📁 文件说明

### 核心模块
- `arxiv_fetcher.py` - arXiv API 查询模块，支持论文获取和去重
- `arxiv_to_csv.py` - CSV 存储模块，处理数据的保存、加载和搜索
- `arxiv_scheduler.py` - 调度器脚本，提供命令行接口

### 配置文件
- `.env` - 环境变量配置（可选）

### 数据文件
- `arxiv_papers.csv` - 默认的论文数据存储文件
- `arxiv_papers_export.md` - 导出的 Markdown 文件
- `processed_arxiv_ids.txt` - 已处理的论文 ID 历史记录

## 🛠️ 安装依赖

```bash
pip install requests python-dotenv
```

## 📖 使用方法

### 1. 基本使用 - 获取最新论文

```bash
# 获取默认类别（cs.CV, cs.AI, cs.LG）的最新 20 篇论文
python3 arxiv_scheduler.py

# 自定义类别和数量
python3 arxiv_scheduler.py --categories cs.CL,cs.NE --max-papers 10
```

### 2. 搜索特定主题

```bash
# 搜索特定关键词的论文
python3 arxiv_scheduler.py --search "transformer" --max-papers 5
```

### 3. 查看统计信息

```bash
# 显示当前 CSV 文件的统计信息
python3 arxiv_scheduler.py --stats
```

### 4. 本地搜索

```bash
# 在已保存的 CSV 中搜索关键词
python3 arxiv_scheduler.py --search-csv "attention"
```

### 5. 导出为 Markdown

```bash
# 导出到 Markdown 文件
python3 arxiv_scheduler.py --export-markdown my_papers.md
```

## ⚙️ 配置选项

### 命令行参数

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--categories` | `-c` | `cs.CV,cs.AI,cs.LG` | 论文类别，用逗号分隔 |
| `--max-papers` | `-m` | `20` | 最大获取论文数 |
| `--csv-file` | `-f` | `arxiv_papers.csv` | CSV 文件名 |
| `--search` | `-s` | - | 搜索关键词 |
| `--stats` | - | - | 显示统计信息 |
| `--search-csv` | - | - | 在 CSV 中搜索 |
| `--export-markdown` | - | - | 导出到 Markdown 文件 |

### 常用 arXiv 类别

| 类别 | 说明 | 类别 | 说明 |
|------|------|------|------|
| `cs.AI` | 人工智能 | `cs.CV` | 计算机视觉 |
| `cs.LG` | 机器学习 | `cs.CL` | 计算语言学 |
| `cs.NE` | 神经网络 | `cs.RO` | 机器人学 |
| `stat.ML` | 统计机器学习 | `cs.IR` | 信息检索 |

## 📊 数据格式

### CSV 文件字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `arxiv_id` | 论文唯一ID | `2512.02020` |
| `title` | 论文标题 | `EfficientFlow: Efficient...` |
| `authors` | 作者列表（分号分隔） | `Author1; Author2; Author3` |
| `summary` | 论文摘要 | `Generative modeling has...` |
| `published_date` | 发布日期 | `2025-12-01T18:59:59Z` |
| `updated_date` | 更新日期 | `2025-12-01T18:59:59Z` |
| `categories` | 类别列表（分号分隔） | `cs.AI; cs.CV; cs.LG` |
| `pdf_url` | PDF 链接 | `https://arxiv.org/pdf/...` |
| `source_url` | 原文链接 | `http://arxiv.org/abs/...` |
| `created_at` | 保存时间 | `2025-12-02 23:35:18` |

## 🔄 定时使用

### 使用 cron 定时获取

```bash
# 编辑 crontab
crontab -e

# 每天早上 8 点获取最新论文
0 8 * * * cd /path/to/arxiv && python3 arxiv_scheduler.py

# 每 6 小时获取一次
0 */6 * * * cd /path/to/arxiv && python3 arxiv_scheduler.py
```

### 使用 systemd 定时器

创建 `/etc/systemd/system/arxiv-crawler.timer`:

```ini
[Unit]
Description=arXiv paper crawler timer

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

创建 `/etc/systemd/system/arxiv-crawler.service`:

```ini
[Unit]
Description=arXiv paper crawler

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/arxiv
ExecStart=/usr/bin/python3 arxiv_scheduler.py
```

启用服务：
```bash
sudo systemctl enable arxiv-crawler.timer
sudo systemctl start arxiv-crawler.timer
```

## 📈 使用示例

### 示例 1: 获取计算机视觉论文

```bash
python3 arxiv_scheduler.py \
  --categories cs.CV \
  --max-papers 15 \
  --csv-file cv_papers.csv
```

### 示例 2: 跟踪特定研究方向

```bash
# 搜索 GPT 相关论文
python3 arxiv_scheduler.py --search "GPT" --max-papers 10

# 在已有数据中搜索
python3 arxiv_scheduler.py --search-csv "transformer"
```

### 示例 3: 生成周报

```bash
# 获取本周新论文
python3 arxiv_scheduler.py --max-papers 50

# 导出为 Markdown 格式
python3 arxiv_scheduler.py --export-markdown weekly_report.md
```

## 🛡️ 注意事项

1. **速率限制**: 工具默认 2 秒间隔，遵守 arXiv 的访问限制
2. **存储空间**: 长期运行会产生大量数据，注意磁盘空间
3. **网络依赖**: 需要稳定的网络连接来获取 arXiv 数据
4. **数据备份**: 建议定期备份 CSV 文件

## 🐛 故障排除

### 常见问题

1. **网络错误**: 检查网络连接和防火墙设置
2. **API 限制**: 如遇到 429 错误，增加 `delay_seconds` 参数
3. **编码问题**: 确保 CSV 文件使用 UTF-8 编码
4. **权限问题**: 确保有写入当前目录的权限

### 调试模式

在代码中添加调试输出：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 技术支持

如果遇到问题，可以：
1. 检查网络连接
2. 查看 arXiv API 状态页面
3. 查看生成的日志文件
4. 检查 CSV 文件是否损坏

---

## 🔄 更新日志

- **v1.0**: 基础功能实现
- **v1.1**: 添加搜索和导出功能
- **v1.2**: 优化去重机制和错误处理