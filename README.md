# The Awesome Index

按 Star 数排序的 GitHub `awesome-*` 系列列表导航站。数据通过 GitHub Actions **每日自动刷新**，无需手动维护。

- 🌐 静态站点：`index.html`（纯 HTML/CSS/JS，无构建步骤）
- 🔄 数据源：`data/repos.json`（由脚本生成，页面运行时 `fetch` 读取）
- 🤖 自动更新：`.github/workflows/update-data.yml`（每天 UTC 01:00 / 北京时间 09:00 运行）

---

## 目录结构

```
.
├── .github/workflows/update-data.yml   # 定时任务：抓取数据并提交
├── scripts/fetch_data.py               # 调用 GitHub API 抓取 awesome-list 仓库
├── data/repos.json                     # 生成的数据文件（首次已附带一份快照）
├── index.html                          # 站点页面
└── README.md
```

## 快速部署（GitHub Pages）

1. 新建一个 GitHub 仓库，把本项目所有文件推送上去（保留 `.github` 目录）。

   ```bash
   git init
   git add .
   git commit -m "init: awesome index"
   git branch -M main
   git remote add origin https://github.com/<你的用户名>/<仓库名>.git
   git push -u origin main
   ```

2. 打开仓库 **Settings → Pages**，Source 选择 `Deploy from a branch`，分支选 `main`，目录选 `/ (root)`，保存。
   几分钟后即可通过 `https://<你的用户名>.github.io/<仓库名>/` 访问。

3. 打开仓库 **Settings → Actions → General**，在 "Workflow permissions" 下选择
   **Read and write permissions**（否则定时任务无法提交更新后的 `data/repos.json`）。

4.（可选）想立刻测试数据刷新，进入 **Actions → Update repo data → Run workflow** 手动触发一次。

完成以上步骤后，站点会每天自动重新抓取最新的 Star 排名，Actions 提交新数据 → Pages 自动重新部署，全程无需人工干预。

## 本地预览

数据用 `fetch()` 读取，需要通过 HTTP 服务打开（不能直接双击 `index.html`）：

```bash
python3 -m http.server 8000
# 然后访问 http://localhost:8000
```

## 手动刷新数据

```bash
pip install --upgrade pip   # 无第三方依赖，仅用标准库
python3 scripts/fetch_data.py
```

生成的 `GITHUB_TOKEN` 是可选的（未认证请求上限为 60 次/小时，通常够用）；如果频繁触发限流，
可以设置一个 [Personal Access Token](https://github.com/settings/tokens)：

```bash
GITHUB_TOKEN=ghp_xxx python3 scripts/fetch_data.py
```

在 GitHub Actions 中，`update-data.yml` 会自动使用内置的 `secrets.GITHUB_TOKEN`，无需额外配置。

## 自定义

- **抓取范围**：修改 `scripts/fetch_data.py` 里的 `QUERY`（默认 `topic:awesome-list`）和 `MAX_PAGES`。
  比如改成 `QUERY = "awesome in:name"` 可以按仓库名而非话题标签搜索。
- **更新频率**：修改 `.github/workflows/update-data.yml` 里的 `cron` 表达式。
- **视觉风格**：所有样式在 `index.html` 的 `<style>` 内，改 `:root` 里的 CSS 变量即可换配色。

## 许可

数据来自 GitHub 公开 API，遵循 GitHub 服务条款；代码部分可自由使用和修改。
