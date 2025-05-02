# LLMClient

轻量级LLM API客户端库，基于Python开发，支持缓存、重试和详细日志记录功能。

作者: Leo <marticle.ios@gmail.com>

[English Version](README_EN.md) | [中文版](README_ZH.md)

## 特性

- **轻量便捷**：简洁的API设计，易于集成和使用
- **环境变量控制**：通过环境变量灵活配置所有功能
- **SQLite缓存**：内置高效的本地缓存机制，减少重复API调用
- **自动重试**：内置智能重试机制，应对网络波动和临时错误
- **详细日志**：可配置的详细日志记录，支持调试模式

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/llmclient.git
cd llmclient

# 安装依赖
pip install -r requirements.txt

# 安装库（开发模式）
pip install -e .
```

## 环境变量配置

创建`.env`文件并配置以下环境变量：

```
# API配置
LLM_API_BASE=https://api.deepseek.com/v1
LLM_API_KEY=your_api_key_here
LLM_MODEL=deepseek-chat
LLM_MAX_TOKENS=8000
LLM_TEMPERATURE=1.0

# 缓存配置
LLM_CACHE_ENABLED=true
LLM_CACHE_PATH=~/.llmclient/cache.db
LLM_CACHE_EXPIRY_DAYS=30

# 调试配置
LLM_DEBUG=false
LLM_DEBUG_DIR=~/.llmclient/logs

# 重试配置
LLM_RETRY_ATTEMPTS=3
LLM_RETRY_MIN_WAIT=2
LLM_RETRY_MAX_WAIT=10
```

## 快速开始

### 基本用法

```python
from llmclient import LLMClient

# 创建客户端（使用环境变量配置）
client = LLMClient()

# 发送简单请求
response = client.completion("请用一句话介绍人工智能。")
print(response)
```

### 自定义配置

```python
from llmclient import LLMClient, LLMConfig

# 创建自定义配置
config = LLMConfig(
    api_base="https://api.deepseek.com/v1",
    api_key="your_api_key_here",
    model="deepseek-chat",
    max_tokens=2000,
    temperature=0.7,
    cache_enabled=True,
    debug_enabled=True
)

# 使用自定义配置创建客户端
client = LLMClient(config)

# 发送请求
response = client.completion("请列举三种常见的机器学习算法。")
print(response)
```

### 多轮对话

```python
from llmclient import LLMClient

client = LLMClient()

# 构建对话历史
messages = [
    {"role": "user", "content": "你好，我想了解一下深度学习。"},
    {"role": "assistant", "content": "你好！深度学习是机器学习的一个分支，它使用多层神经网络来模拟人脑的学习过程。有什么具体方面你想了解的吗？"},
    {"role": "user", "content": "请介绍一下CNN和RNN的区别。"}
]

response = client.chat_completion(messages)
print(response)
```

### 使用工具函数

```python
from llmclient import LLMClient
from llmclient.utils import format_prompt, extract_json, chunk_text

client = LLMClient()

# 使用模板
template = """请为一家{industry}公司起一个名字，要求：
1. 名字要简洁易记
2. 能反映公司的行业特点
3. 有创意和现代感"""

prompt = format_prompt(template, industry="人工智能")
response = client.completion(prompt)
print(response)

# 分割长文本
long_text = "这是一段非常长的文本..." * 100
chunks = chunk_text(long_text, chunk_size=4000, overlap=200)
for chunk in chunks:
    response = client.completion(chunk)
    print(response)
```

## 高级功能

### 缓存管理

```python
from llmclient import LLMClient

client = LLMClient()

# 清理过期缓存
deleted_count = client.clear_cache()
print(f"已清理 {deleted_count} 条过期缓存")

# 清理指定天数前的缓存
deleted_count = client.clear_cache(days=7)
print(f"已清理 {deleted_count} 条7天前的缓存")
```

### 调试模式

```python
from llmclient import LLMClient

client = LLMClient()

# 启用调试模式
client.set_debug(True)

# 发送请求（将记录详细日志）
response = client.completion("这是一个测试请求")

# 禁用调试模式
client.set_debug(False)
```

## 示例脚本

查看 `example.py` 获取更多使用示例。

```bash
python example.py
```

## 依赖

- requests: HTTP请求
- tenacity: 重试机制
- python-dotenv: 环境变量加载
- sqlite3: 内置缓存数据库

## 许可证

MIT