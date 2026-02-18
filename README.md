# 🚀 Life-Workflow-Skills

> 将生活中重复性的工作流转化为可复用的 AI Skills，实现个人效率自动化。

## 📖 项目简介

本项目基于个人日常生活与工作中的高频重复场景，将其标准化并封装为 AI Skills。通过调用这些技能，您可以快速自动化处理文档生成、数据分析、流程审批等任务，释放精力专注于更有价值的工作。

## 🛠️ 环境准备

- **推荐工具**: [OpenCode](https://opencode.ai/) (或其他支持 Skills 的 AI 编程助手)
  - *推荐理由*: 内置免费模型，开箱即用，无需额外配置 API Key。
- **项目结构**: 确保您的项目根目录下包含 `skills` 文件夹。

## 📦 安装与配置

1. **下载 Skills**: 克隆或下载本仓库中的所有技能文件。
2. **部署文件**: 将下载的 skills 文件放入项目根目录下的 `skills` 文件夹中。
   ```bash
   # 示例目录结构
   .
   ├── skills/
   │   ├── thesis-assistant/
   │   └── ...
   └── ...
   ```



## 💡 使用方法

在 OpenCode 或兼容的 AI 助手对话框中，直接调用对应的 Skill 名称即可。

### 使用示例

假设您需要撰写一篇论文，可以使用 `thesis-assistant` 技能。请在对话框中输入以下指令：

```text
请用 skills 文件夹里的 thesis-assistant 这个 skill 帮我写一篇《XXXXXX》，以 md 格式放在根目录里
```

