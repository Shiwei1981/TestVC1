# 网页算命应用

一个最小可运行（MVP）的 Flask + SQLite + Azure OpenAI 网页算命应用，支持注册/登录、调用 `chat.completions` 获取占卜结果，并保留最近 30 条历史记录。

## 功能亮点
- ✅ 注册 / 登录 / 退出，会话基于 Flask `session`
- 🔐 密码使用 `werkzeug.security` 进行哈希存储
- 🔮 `/divine` 接口通过 Azure OpenAI `gpt-5.2` 生成算命结果
- 🗂️ SQLite `app.db` 保存用户与占卜历史
- 🗒️ 前端采用 Jinja + 原生 JS，提交后即时更新历史列表

## 技术栈
- Flask 3.x（Web 框架）
- SQLite（本地文件数据库）
- Azure OpenAI Chat Completions（openai Python SDK 的 `AzureOpenAI` 客户端）
- HTML5 / CSS3 / 原生 JavaScript（前端）

## 快速开始
1. **克隆并进入项目**
	```bash
	git clone <your-repo-url>
	cd TestVC1
	```
2. **可选：创建虚拟环境**
	```bash
	python3 -m venv .venv
	source .venv/bin/activate
	```
3. **安装依赖**
	```bash
	pip install -r requirements.txt
	```
4. **配置环境变量**
	```bash
	cp .env.example .env
	# 编辑 .env，填入 Azure OpenAI 相关参数与 SECRET_KEY
	```
5. **初始化数据库并启动服务**（首次运行会自动建表）
	```bash
	python3 app.py
	```
	服务器默认监听 `http://0.0.0.0:8000`。

## 关键环境变量（.env）
| 变量 | 描述 |
| --- | --- |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI 资源 Endpoint，如 `https://xxx.openai.azure.com/` |
| `AZURE_OPENAI_KEY` | 对应资源的 API Key |
| `AZURE_OPENAI_DEPLOYMENT` | 模型部署名称，例如 `gpt-5.2` |
| `AZURE_OPENAI_API_VERSION` | API 版本，默认 `2024-12-01-preview` |
| `SECRET_KEY` | Flask Session 密钥，需随机字符串 |

## 项目结构
```
.
├── app.py
├── requirements.txt
├── .env / .env.example
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── register.html
├── static/
│   ├── app.js
│   └── style.css
└── README.md
```

## 发布到 GitHub
1. 初始化仓库并提交：
	```bash
	git init
	git add .
	git commit -m "feat: add fortune app MVP"
	```
2. 在 GitHub 新建仓库（例如 `fortune-web`），复制远程地址。
3. 关联远程并推送：
	```bash
	git remote add origin git@github.com:<your-account>/fortune-web.git
	git push -u origin main
	```

完成以上步骤就能在任意支持 Python3 的环境中运行并演示网页算命应用。
