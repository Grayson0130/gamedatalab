# 开发、复现与发布

## 环境

核心只依赖 Python 标准库与内置 SQLite。目标 Python 3.11–3.13，CI 为三个版本配置矩阵；本次交付的本地实测版本以 [验证报告](../VALIDATION.md) 为准，不能把尚未运行的远程 CI 写成通过。

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m gamedatalab
python -m unittest discover -s tests -v
python -m pip install -r requirements-docs.txt
python scripts/build_site.py
python scripts/check_links.py
python scripts/check_reproducibility.py
```

文档构建用锁定的 Python-Markdown。核心代码不依赖此包；没有为演示引入 pandas、GPU 或云 SDK。若需更多版本适配，应重新测试并更新支持矩阵。

## 输出与幂等

`python -m gamedatalab` 默认覆盖 `reports/demo/` 中同名输出，不删除其他文件。试验参数建议用 `--output reports/my-demo`。随机种子、截止日、输入哈希和版本保存在输出中；不注入当前时间，以便字节级比较。

文档构建会清空并重建 `site/`，它是专用生成目录，不要手动存工作文件。所有文档和静态资源复制进这个目录，链接重写为 HTML。搜索使用嵌入式索引，无 CDN 和后台；索引只包含每页标题与前 900 字摘要，不是全文搜索引擎。

## GitHub Pages

`.github/workflows/pages.yml` 在 main push 或手动触发时构建并部署 `site/`。仓库 Settings → Pages 的 Source 需选择 **GitHub Actions**；运行账号须具备相应权限。功能分支仅执行 CI，不自动替换主站。

未开启 Pages 或权限不足时 workflow 会失败；查看 Actions 日志处理，不能仅凭配置文件存在宣称网站上线。项目已有 URL 为 <https://grayson0130.github.io/gamedatalab/>，当前线上状态不由本地构建保证。

## 打包与手动推送

```bash
python scripts/package.py
```

输出 `dist/gamedatalab-2026-v0.2.0.zip`，包含源码、文档、样例与已构建离线站点，排除 Git 历史、虚拟环境和缓存；包内 `PACKAGE-MANIFEST.json` 提供逐文件 SHA-256。压缩包中的网页入口为 `gamedatalab/site/index.html`，可直接打开或用 HTTP 服务预览。

若远程推送能力可用，应先推功能分支并审查差异；本项目不使用强制推送。用户本机有仓库权限时，可在真实本地 Git checkout 执行：

```bash
git switch -c update/2026-complete
git add .
git commit -m "Expand game analytics docs and reproducible lab for 2026"
git push -u origin update/2026-complete
```

压缩包不含 `.git`；不要将 `site/`、`dist/` 或私人数据意外提交。若已在同名分支则无需再创建。应在本机完成 GitHub 登录，不在聊天里粘贴密码、token 或私钥。

## 扩展真实数据

当前 CLI 仅生成合成数据，无导入任意 CSV 的公开命令。新增真实适配器时实现用户/订单粒度、时间戳、币种、同意与删除流程，并独立验证。生产事件规模需流式摄取和增量计算，不能把所有事件无限累积在内存。
