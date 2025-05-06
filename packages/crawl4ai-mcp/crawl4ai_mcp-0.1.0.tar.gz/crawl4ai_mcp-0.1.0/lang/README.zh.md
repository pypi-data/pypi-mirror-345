# Web Crawler MCP

[![English](https://img.shields.io/badge/lang-en-blue.svg)](../README.md) [![中文](https://img.shields.io/badge/lang-zh-blue.svg)](README.zh.md) [![हिंदी](https://img.shields.io/badge/lang-hi-blue.svg)](README.hi.md) [![Español](https://img.shields.io/badge/lang-es-blue.svg)](README.es.md) [![Français](https://img.shields.io/badge/lang-fr-blue.svg)](README.fr.md) [![العربية](https://img.shields.io/badge/lang-ar-blue.svg)](README.ar.md) [![বাংলা](https://img.shields.io/badge/lang-bn-blue.svg)](README.bn.md) [![Русский](https://img.shields.io/badge/lang-ru-blue.svg)](README.ru.md) [![Português](https://img.shields.io/badge/lang-pt-blue.svg)](README.pt.md) [![Bahasa Indonesia](https://img.shields.io/badge/lang-id-blue.svg)](README.id.md)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

一个通过 MCP（机器对话协议）与 AI 助手集成的强大网络爬虫工具。该项目允许您爬取网站并保存内容 [...]

## 📋 功能

- 可配置深度的网站爬取
- 支持内部和外部链接
- 生成结构化的 Markdown 文件
- 通过 MCP 与 AI 助手原生集成
- 详细的爬取结果统计
- 错误和未找到页面处理

## 🚀 安装

### 前提条件

- Python 3.9 或更高版本

### 安装步骤

1. 克隆此仓库：

```bash
git clone laurentvv/crawl4ai-mcp
cd crawl4ai-mcp
```

2. 创建并激活虚拟环境：

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python -m venv .venv
source .venv/bin/activate
```

3. 安装所需依赖：

```bash
pip install -r requirements.txt
```

## 🔧 配置

### AI 助手的 MCP 配置

要将此爬虫与 VScode Cline 等 AI 助手一起使用，请配置您的 `cline_mcp_settings.json` 文件：

```json
{
  "mcpServers": {
    "crawl": {
      "command": "PATH\\TO\\YOUR\\ENVIRONMENT\\.venv\\Scripts\\python.exe",
      "args": [
        "PATH\\TO\\YOUR\\PROJECT\\crawl_mcp.py"
      ],
      "disabled": false,
      "autoApprove": [],
      "timeout": 600
    }
  }
}
```

将 `PATH\\TO\\YOUR\\ENVIRONMENT` 和 `PATH\\TO\\YOUR\\PROJECT` 替换为您系统上的适当路径。

#### 具体示例 (Windows)

```json
{
  "mcpServers": {
    "crawl": {
      "command": "C:\\Python\\crawl4ai-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "D:\\Python\\crawl4ai-mcp\\crawl_mcp.py"
      ],
      "disabled": false,
      "autoApprove": [],
      "timeout": 600
    }
  }
}
```

## 🖥️ 使用方法

### 通过 AI 助手使用（通过 MCP）

在 AI 助手中配置完成后，您可以使用以下语法要求助手执行爬取：

```
能否爬取网站 https://example.com，深度为 2？
```

助手将使用 MCP 协议以指定参数运行爬虫工具。

### 与 Claude 一起使用的示例

配置 MCP 工具后，您可以向 Claude 发出的请求示例：

- **简单爬取**：「能否爬取网站 example.com 并给我总结？」
- **带选项的爬取**：「能否以深度 3 爬取 https://example.com 并包含外部链接？」
- **自定义输出的爬取**：「能否爬取博客 example.com 并将结果保存为'blog_analysis.md'？」

## 📁 结果结构

爬取结果保存在项目根目录的 `crawl_results` 文件夹中。每个结果文件都以 Markdown 格式保存，结构如下：

```markdown
# https://example.com/page

## 元数据
- 深度：1
- 时间戳：2023-07-01T12:34:56

## 内容
从页面提取的内容...

---
```

## 🛠️ 可用参数

爬虫工具接受以下参数：

| 参数 | 类型 | 描述 | 默认值 |
|-----------|------|-------------|---------------|
| url | 字符串 | 要爬取的 URL（必需） | - |
| max_depth | 整数 | 最大爬取深度 | 2 |
| include_external | 布尔值 | 包含外部链接 | false |
| verbose | 布尔值 | 启用详细输出 | true |
| output_file | 字符串 | 输出文件路径 | 自动生成 |

## 📊 结果格式

工具返回包含以下内容的摘要：
- 爬取的 URL
- 生成文件的路径
- 爬取持续时间
- 处理页面的统计信息（成功、失败、未找到、访问被禁止）

结果保存在项目的 `crawl_results` 目录中。

## 🤝 贡献

欢迎贡献！随时提出问题或提交拉取请求。

## 📄 许可证

该项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。