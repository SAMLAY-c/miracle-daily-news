# Arxiv 论文自动抓取 - 定时任务配置指南

## 🚀 快速开始

### 方法1: macOS/Linux 定时任务 (推荐)

#### 1. 创建 cron 任务
```bash
# 编辑 cron 任务
crontab -e

# 添加以下行，每2小时运行一次
0 */2 * * * cd /Users/sam/Desktop/arxiv && /usr/bin/python3 arxiv_feishu_fetcher.py >> arxiv_cron.log 2>&1

# 或者每天早上8点运行一次
0 8 * * * cd /Users/sam/Desktop/arxiv && /usr/bin/python3 arxiv_feishu_fetcher.py >> arxiv_daily.log 2>&1
```

#### 2. 查看和调试
```bash
# 查看 cron 任务列表
crontab -l

# 查看运行日志
tail -f arxiv_cron.log

# 手动测试脚本
cd /Users/sam/Desktop/arxiv && python3 arxiv_feishu_fetcher.py
```

### 方法2: 使用 system 服务 (更稳定)

#### 1. 创建服务配置文件
```bash
# 创建服务配置
sudo nano /Library/LaunchDaemons/com.user.arxivfetcher.plist
```

#### 2. 服务配置内容
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.arxivfetcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/sam/Desktop/arxiv/arxiv_feishu_fetcher.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/sam/Desktop/arxiv</string>
    <key>StartInterval</key>
    <integer>7200</integer>  <!-- 2小时 = 7200秒 -->
    <key>StandardOutPath</key>
    <string>/Users/sam/Desktop/arxiv/arxiv_daemon.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/sam/Desktop/arxiv/arxiv_error.log</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

#### 3. 启动和管理服务
```bash
# 加载服务
sudo launchctl load /Library/LaunchDaemons/com.user.arxivfetcher.plist

# 启动服务
sudo launchctl start com.user.arxivfetcher

# 查看服务状态
sudo launchctl list | grep arxivfetcher

# 停止服务
sudo launchctl stop com.user.arxivfetcher

# 卸载服务
sudo launchctl unload /Library/LaunchDaemons/com.user.arxivfetcher.plist
```

## 🔧 脚本配置选项

### 修改抓取频率和范围
编辑 `arxiv_feishu_fetcher.py` 中的 `main()` 函数:

```python
def main():
    fetcher = ArxivFetcher()

    # 抓取配置
    max_results = 50        # 每次最多获取50篇论文
    days_back = 3          # 获取最近3天的论文

    # 指定特定分类 (可选)
    categories = ['cs.CV', 'cs.LG']  # 只获取CV和LLM论文

    # 执行抓取任务
    fetcher.run(max_results=max_results, categories=categories, days_back=days_back)
```

### 自定义 AI 领域分类
```python
# 在 ArxivFetcher.__init__ 中修改分类映射
self.AI_CATEGORIES = {
    'cs.CV': 'CV (计算机视觉)',
    'cs.CL': 'NLP (自然语言处理)',
    'cs.LG': 'LLM (大语言模型)',
    'cs.AI': 'LLM (大语言模型)',
    'cs.RO': 'RL (强化学习)',
    'cs.MM': 'Multimodal (多模态)',
    # 添加更多分类...
}
```

## 📊 监控和维护

### 1. 日志文件
- `arxiv_cron.log`: 定时任务执行日志
- `arxiv_fetcher.log`: 脚本运行日志
- `arxiv_daemon.log`: 系统服务日志
- `arxiv_error.log`: 错误日志

### 2. 数据文件
- `processed_arxiv_ids.txt`: 已处理的论文ID集合
- `last_fetch_time.txt`: 上次抓取时间

### 3. 常用监控命令
```bash
# 查看最新抓取的论文
grep "成功处理" arxiv_cron.log | tail -10

# 检查错误
grep "ERROR" arxiv_fetcher.log | tail -5

# 查看抓取统计
grep "总共获取\|其中新论文" arxiv_cron.log | tail -10
```

## ⚠️ 注意事项

### 1. Arxiv API 限制
- **速率限制**: 每秒最多1次请求
- **带宽限制**: 避免过于频繁的请求
- **遵守规则**: 脚本已内置 `time.sleep(1)` 遵守限制

### 2. 飞书 API 限制
- **批量写入**: 每次最多500条记录
- **频率限制**: 避免过于频繁的写入操作
- **字符编码**: 已处理UTF-8编码问题

### 3. 系统资源
- **磁盘空间**: 日志文件会逐渐增大，定期清理
- **网络连接**: 确保网络稳定
- **Python环境**: 确保依赖库 `requests` 安装

## 🚨 故障排除

### 常见问题和解决方案

#### 1. cron 任务不执行
```bash
# 检查 cron 服务状态
sudo launchctl list | grep cron

# 重启 cron 服务
sudo launchctl unload /System/Library/LaunchDaemons/com.apple.vix.cron.plist
sudo launchctl load /System/Library/LaunchDaemons/com.apple.vix.cron.plist
```

#### 2. Python 路径问题
```bash
# 查找 Python3 路径
which python3

# 使用完整路径
/usr/bin/python3 /Users/sam/Desktop/arxiv/arxiv_feishu_fetcher.py
```

#### 3. 权限问题
```bash
# 确保脚本有执行权限
chmod +x arxiv_feishu_fetcher.py

# 检查日志文件权限
ls -la *.log
```

#### 4. 网络连接问题
```bash
# 测试 Arxiv API 连接
curl "http://export.arxiv.org/api/query?search_query=cat:cs.CV&max_results=1"

# 测试飞书 API 连接
curl -X GET "https://open.feishu.cn/open-apis/bitable/v1/apps/DdCZbBA7baN2SjsUt5McCnrnnsc/tables/tblb9sbMaoghEbWW/fields" \
  -H "Authorization: Bearer t-g104c303A6373MHT63OJMF6KSKG4SWVPZU4D47NU"
```

## 📈 性能优化建议

### 1. 批量处理优化
- 增加每次获取的论文数量 (`max_results`)
- 减少抓取频率，增加每次抓取量

### 2. 存储优化
- 定期清理旧的日志文件
- 压缩历史数据文件

### 3. 监控优化
- 设置邮件通知重要错误
- 定期检查去重机制是否正常工作

## 🎯 进阶功能

### 1. 智能去重增强
- 添加论文标题相似度检测
- 基于作者和摘要的重复检测

### 2. 内容质量筛选
- 添加论文引用数过滤
- 基于会议/期刊质量的筛选

### 3. 自动分类增强
- 使用自然语言处理自动分类
- 基于论文摘要的关键词提取

### 4. 通知功能
- 重要论文邮件通知
- Slack/微信机器人集成

---

## 📞 获取帮助

如遇到问题：
1. 查看日志文件定位具体错误
2. 运行测试脚本 `test_simple.py` 验证连接
3. 检查网络和API配置
4. 查阅 Arxiv API 官方文档: https://info.arxiv.org/help/api/index.html