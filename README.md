# 良师教育自动学习助手

**开源免费 | 仅供学习交流使用 | 禁止商业用途**

一个帮助学生自动化完成良师教育平台网课学习的工具，支持自动刷视频、AI智能答题等功能。

> **适配说明**：本脚本专为湖南外国语职业学院（huwai.ls365.net）开发并测试，100%支持该校平台。其他使用良师教育平台（ls365.net）的学校理论上也可使用，但由于各校平台可能存在细微差异，可能需要微调部分代码。平台整体模板应该是一致的。

## 目录

- [功能特点](#功能特点)
- [快速开始](#快速开始)
- [详细使用说明](#详细使用说明)
- [配置说明](#配置说明)
- [打包为EXE](#打包为exe)
- [适配说明](#适配说明)
- [常见问题](#常见问题)
- [注意事项](#注意事项)

## 功能特点

- 自动刷视频 - 支持多窗口同时播放，自动检测完成并切换
- 智能答题 - 集成多种 AI（Kimi、ChatGPT、智谱等）自动答题
- 智能考试 - 自动完成所有未完成的考试，支持AI答题和随机答题
- 倍速播放 - 支持 0.5X~2X 多种播放速度
- 美观界面 - 基于 ttkbootstrap 的现代化 GUI
- 灵活配置 - 丰富的配置选项，满足不同需求
- 一键打包 - 可打包为 exe，无需 Python 环境

## 快速开始

### 方式一：使用 EXE（推荐）

1. **下载程序**
   - 访问 [Releases 页面](https://github.com/145870/ls365autok/releases)
   - 下载最新版本的 `湖南外国语自动学习助手.exe`
   
2. **运行程序**
   - 双击运行 exe 文件
   - 在"配置"选项卡填写学号、密码、网站地址
   - 点击"保存配置"
   - 选择功能并点击"开始"按钮

> 注意：如果需要自行打包，可以运行 `快速打包.bat`

### 方式二：直接运行源码

1. **安装 Python 3.7+**

2. **安装依赖**
   ```bash
   pip install selenium ttkbootstrap openai
   ```

3. **运行程序**
   ```bash
   # GUI 版本（推荐）
   python auto_study_gui_v2.py
   
   # 命令行版本
   python auto_study.py
   ```

## 详细使用说明

### 系统要求

- Windows 7 / 10 / 11 系统
- Chrome 浏览器（程序会自动下载 ChromeDriver）
- 联网环境
- Python 3.7+（如直接运行源码）

### 首次使用

1. 双击运行程序
2. 切换到"配置"选项卡
3. 填写以下信息：
   - **学号**：您的学号
   - **密码**：您的密码
   - **网站地址**：您学校的良师教育平台网址
     - 湖南外国语：`https://huwai.ls365.net/University/User/Student/mycourselist.aspx?m=wdkc`
     - 其他学校格式：`https://学校简称.ls365.net/University/User/Student/mycourselist.aspx?m=wdkc`
   - **AI API Key**（如需使用 AI 答题功能）
4. 点击"保存配置"按钮

### 功能说明

#### 刷视频
- 连续窗口数：同时打开多个视频窗口进行学习（建议3-5个）
- 播放倍速：1X、1.25X、1.5X、2X 可选
- 自动检测视频完成并切换到下一个

#### 答题
- AI答题：使用 AI 自动回答问题（需配置 AI API）
- 随机答题：随机选择答案（准确率较低）
- 支持自动提交和不及格重做

#### 考试
- AI答题：使用 AI 自动回答考试题目（需配置 AI API）
- 随机答题：随机选择答案（准确率较低）
- 自动提交：完成后自动提交考试
- 批量处理：自动完成所有未完成的考试

### 使用步骤

1. 启动程序
2. 在"主程序"选项卡选择功能
3. 点击对应的"开始"按钮
4. 查看运行日志了解执行进度
5. 如需停止，点击"停止任务"按钮

## 配置说明

### 配置文件位置

配置文件为 `config.json`，位于程序同目录下。

### 配置文件示例

```json
{
  "website": {
    "url": "https://huwai.ls365.net/University/User/Student/mycourselist.aspx?m=wdkc",
    "username": "你的学号",
    "password": "你的密码"
  },
  "browser": {
    "type": "chrome",
    "window_width": 1920,
    "window_height": 1080,
    "headless": false
  },
  "automation": {
    "enable_delays": false,
    "enable_duration_check": false,
    "element_timeout": 10,
    "page_load_timeout": 30,
    "video_speed": "2X",
    "video_wait_after_complete": 10,
    "concurrent_videos": 9
  },
  "homework": {
    "use_ai": true,
    "auto_submit": true,
    "min_passing_score": 60,
    "retry_if_failed": true
  },
  "exam": {
    "use_ai": true,
    "auto_submit": true,
    "answer_delay_min": 0.5,
    "answer_delay_max": 1.5
  },
  "ai": {
    "provider": "openai",
    "openai_api_key": "your-api-key-here",
    "openai_base_url": "https://api.moonshot.cn/v1",
    "openai_model": "moonshot-v1-8k",
    "zhipu_api_key": "your-zhipu-api-key-here",
    "zhipu_model": "glm-4-flash"
  },
  "debug": {
    "highlight_elements": true
  }
}
```

### 配置项详解

#### 网站配置 (website)

- `url`: 学习平台网址
  - 湖南外国语：`https://huwai.ls365.net/University/User/Student/mycourselist.aspx?m=wdkc`
  - 其他学校格式：`https://学校简称.ls365.net/University/User/Student/mycourselist.aspx?m=wdkc`
- `username`: 您的学号
- `password`: 您的密码

#### 浏览器配置 (browser)

- `type`: 浏览器类型（目前仅支持 "chrome"）
- `window_width` / `window_height`: 浏览器窗口大小（默认 1920x1080）
- `headless`: 无头模式
  - `false`: 显示浏览器窗口（推荐，方便监控）
  - `true`: 后台运行，不显示窗口

#### 作业配置 (homework)

- `use_ai`: 是否使用AI答题
  - `true`: 使用AI智能答题（推荐，准确率高）
  - `false`: 随机选择答案（快速但准确率低）
- `auto_submit`: 是否自动提交
  - `true`: 完成后自动提交作业
  - `false`: 完成后需要手动确认
- `min_passing_score`: 及格分数（默认60分）
- `retry_if_failed`: 是否重做不及格作业
  - `true`: 自动重做分数低于及格线的作业
  - `false`: 跳过不及格的作业

#### 考试配置 (exam)

- `use_ai`: 是否使用AI答题
  - `true`: 使用AI智能答题（推荐，准确率高）
  - `false`: 随机选择答案（快速但准确率低）
- `auto_submit`: 是否自动提交
  - `true`: 完成后自动提交考试
  - `false`: 完成后需要手动确认
- `answer_delay_min`: 答题最小延迟（秒），模拟人类答题速度
- `answer_delay_max`: 答题最大延迟（秒），模拟人类答题速度

#### AI配置 (ai)

支持两种AI服务：

**方式一：OpenAI 兼容格式（推荐）**

支持：ChatGPT、Kimi、DeepSeek、通义千问等

配置项：
- `provider`: "openai"
- `openai_api_key`: 您的API密钥
- `openai_base_url`: API地址
- `openai_model`: 模型名称

常用配置示例：

1. Kimi (月之暗面)
```json
{
  "provider": "openai",
  "openai_api_key": "your-kimi-api-key",
  "openai_base_url": "https://api.moonshot.cn/v1",
  "openai_model": "moonshot-v1-8k"
}
```

2. DeepSeek
```json
{
  "provider": "openai",
  "openai_api_key": "your-deepseek-api-key",
  "openai_base_url": "https://api.deepseek.com/v1",
  "openai_model": "deepseek-chat"
}
```

3. ChatGPT
```json
{
  "provider": "openai",
  "openai_api_key": "your-openai-api-key",
  "openai_base_url": "https://api.openai.com/v1",
  "openai_model": "gpt-3.5-turbo"
}
```

**方式二：智谱AI**

配置项：
- `provider`: "zhipu"
- `zhipu_api_key`: 您的API密钥
- `zhipu_model`: 模型名称

示例：
```json
{
  "provider": "zhipu",
  "zhipu_api_key": "your-zhipu-api-key",
  "zhipu_model": "glm-4-flash"
}
```

#### 获取API密钥

- Kimi: https://platform.moonshot.cn/
- ChatGPT: https://platform.openai.com/
- 智谱: https://open.bigmodel.cn/
- DeepSeek: https://platform.deepseek.com/
- 通义千问: https://dashscope.aliyun.com/

### 推荐配置组合

**方案一：高准确率模式（推荐）**
```json
{
  "use_ai": true,
  "auto_submit": true,
  "min_passing_score": 60,
  "retry_if_failed": true
}
```

**方案二：快速完成模式（不保证分数）**
```json
{
  "use_ai": false,
  "auto_submit": true,
  "min_passing_score": 60,
  "retry_if_failed": false
}
```

**方案三：谨慎模式（手动检查）**
```json
{
  "use_ai": true,
  "auto_submit": false,
  "min_passing_score": 60,
  "retry_if_failed": true
}
```

## 打包为EXE

### 方法一：使用自动打包脚本（推荐）

1. 运行打包脚本
   ```bash
   # Windows
   快速打包.bat
   
   # 或使用 Python
   python build_exe.py
   ```

2. 等待打包完成
   - 脚本会自动安装 PyInstaller
   - 自动打包程序
   - 生成的 exe 在打包文件夹中

### 方法二：手动打包

1. 安装 PyInstaller
   ```bash
   pip install pyinstaller
   ```

2. 打包命令
   ```bash
   pyinstaller --onefile --windowed --name=自动学习助手 auto_study_gui_v2.py
   ```

3. 参数说明
   - `--onefile`: 打包成单个 exe 文件
   - `--windowed`: 不显示控制台窗口（GUI 程序）
   - `--name`: 指定生成的 exe 文件名

### 打包注意事项

1. **杀毒软件误报**
   - 如果杀毒软件报毒，这是误报
   - 可以添加到白名单或临时关闭杀毒软件

2. **文件大小**
   - 打包后的 exe 文件约 20-50 MB
   - 这是正常的，因为包含了 Python 解释器和所有依赖

3. **跨设备使用**
   - 打包后的 exe 可以在任何 Windows 电脑上运行
   - 不需要安装 Python 和依赖包

## 适配说明

### 湖南外国语职业学院

本脚本专为湖南外国语职业学院（huwai.ls365.net）开发，已经过充分测试，**100%支持**该校平台的所有功能，无需任何修改即可使用。

### 其他良师教育平台学校

如果您的学校也使用良师教育平台（域名格式为 xxx.ls365.net），理论上可以直接使用本脚本：

1. **修改配置文件**
   - 打开 `config.json`
   - 将 `website.url` 改为您学校的良师教育平台地址
   - 格式通常为：`https://学校简称.ls365.net/University/User/Student/mycourselist.aspx?m=wdkc`

2. **测试使用**
   - 运行程序测试是否能正常登录和使用
   - 由于各校平台可能存在细微差异，部分功能可能需要微调
   - 平台整体模板应该是一致的

3. **问题反馈**
   - 如遇到问题，可以在 GitHub 提交 Issue
   - 欢迎提交适配其他学校的代码改进

### 非良师教育平台

如果您的学校使用的不是良师教育平台，则需要：
1. 分析目标平台的页面结构
2. 修改 `auto_study.py` 中的元素定位代码
3. 调整自动化流程逻辑

## 常见问题

### Q: 程序启动后没反应？
A: 第一次启动需要下载 ChromeDriver，请耐心等待

### Q: 浏览器无法打开？
A: 请确认已安装 Chrome 浏览器

### Q: AI 答题不工作？
A: 请检查 API Key 是否正确，网络是否正常

### Q: 考试功能如何使用？
A: 
1. 在主程序页面选择"考试"区域
2. 选择答题模式（AI答题或随机答题）
3. 如果使用AI，选择AI提供商（OpenAI或智谱）
4. 点击"开始考试"按钮
5. 程序会自动完成所有未完成的考试

### Q: 考试会自动提交吗？
A: 根据配置文件中的 `exam.auto_submit` 设置，默认为自动提交。如果设置为 false，需要手动提交

### Q: 配置文件在哪里？
A: 和程序同目录的 config.json

### Q: 我的学校也用良师教育平台，能用吗？
A: 理论上可以！本脚本100%支持湖南外国语职业学院。其他学校只需修改配置中的网站地址，但可能因平台细微差异需要微调

### Q: exe 启动很慢？
A: 这是正常的，第一次启动需要解压文件到临时目录

### Q: 如何减小文件大小？
A: 可以使用虚拟环境，只安装必需的包后再打包

## 注意事项

1. 本工具仅供学习交流使用
2. 请勿用于商业用途
3. 使用本工具产生的任何后果由使用者自行承担
4. 建议合理使用，不要过度依赖自动化工具
5. AI 答题准确率无法保证（约70%-90%，取决于题目难度）
6. 随机答题准确率较低（约25%-50%）
7. 考试功能会自动完成所有未完成的考试，请谨慎使用
8. 考试提交前建议先检查答案，可以设置 `exam.auto_submit` 为 false
9. 请遵守学校相关规定
10. 首次运行需要下载 ChromeDriver，请耐心等待
11. 确保网络连接正常
12. 不要在程序运行时关闭浏览器窗口
13. `config.json` 包含敏感信息，请勿分享给他人

## 项目结构

```
├── auto_study.py          # 核心自动化逻辑（命令行版）
├── auto_study_gui_v2.py   # GUI 版本主程序
├── config.json            # 配置文件
├── build_exe.py           # 打包脚本
├── 快速打包.bat           # Windows 快速打包
├── .gitignore             # Git 忽略规则
└── README.md              # 本文件
```

## 贡献

欢迎提交 Issue 和 Pull Request！

特别欢迎：
- 适配其他学校/平台的代码
- Bug 修复
- 功能改进建议

## 开源协议

本项目完全开源免费，采用 MIT 协议。

## 联系方式

- GitHub Issues: 提交问题和建议
- 讨论区: 参与讨论和交流

---

**免责声明**: 本工具仅供学习交流使用，使用本工具产生的任何后果由使用者自行承担。作者不对使用本工具产生的任何问题负责。

---

如果这个项目对你有帮助，请给一个 Star！

**版本**: 1.0  
**更新日期**: 2025-01-19

