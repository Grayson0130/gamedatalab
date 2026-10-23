# Game Data Lab · 游戏数据科学实践

从游戏问题出发，完成「埋点 → SQL 指标 → 实验与预测 → 决策」的中文学习与作品集仓库。
原仓库源于《游戏领域的数据科学：Data 在 Video Game Industry 中有哪些应用？（第 512 期）》学习笔记；本版重写技术解释，加入独立编写、可复现的教学代码。

**资料核对截至 2026-10-23 · v0.2.0**。方法建议是作者整理；平台事实附官方来源。[2026 更新与证据](docs/updates-2026.md)区分当年变化、延续能力和工程建议。合成数据不代表真实玩家行为、商业收益或行业基准。

## 先运行一个完整案例

Python **3.11–3.13**；核心分析仅用标准库，不需要 API key、云账户或付费服务。在仓库根目录运行：

```bash
python -m gamedatalab
python -m unittest discover -s tests -v
```

默认生成 1,200 名虚构玩家的遥测、UTC 日历日 D1/D7/D30 留存、成熟队列 D0–D30 观测收入、教程实验和时间切分流失基线。输出写入 `reports/demo/`，重复运行会覆盖该目录的同名文件。

```bash
python -m gamedatalab --users 3000 --seed 7 --output reports/my-demo
```

Windows 如果没有 `python` 命令，改用 `py -3`。无需先安装本项目。
阅读预生成的 [结果报告](reports/demo/README.md) 和 [机器可读结果](reports/demo/summary.json)。输入 CSV 及哈希随包提供，分析不需要联网。

## 学习地图

| 路线 | 文档 | 可交付成果 |
| --- | --- | --- |
| 数据基础 | [埋点与数据契约](docs/telemetry.md) · [指标字典](docs/metrics.md) | 事件清单、验收口径 |
| 增长与收入 | [用户获取](docs/user-acquisition.md) · [变现与 LTV](docs/monetization-ltv.md) | 渠道成熟队列收益表 |
| 玩家健康 | [留存、流失与欺诈](docs/retention-churn-fraud.md) | 留存队列、无未来泄漏基线 |
| 因果与产品 | [实验设计](docs/experimentation.md) · [数据驱动设计](docs/data-driven-design.md) | 可审查实验方案 |
| 个性化与 AI | [推荐系统](docs/recommendation.md) · [AI 与本地化评估](docs/ai-evaluation.md) | 排序评估方案、评测集 |
| 工程化 | [现代数据栈](docs/modern-stack-2026.md) · [治理与隐私](docs/governance.md) | 架构取舍、删除流程 |
| 求职展示 | [职业路线](docs/career.md) · [作品集](portfolio/README.md) | 项目复现与决策摘要 |
| 跟进时效 | [2026 更新](docs/updates-2026.md) · [来源清单](docs/sources.md) | 可追溯证据 |

## 目录与验证

```text
gamedatalab/     数据生成器、指标计算与 CLI
sql/             可直接审查的 SQLite SQL
tests/           口径、边界和回归测试
data/            数据契约与合成数据说明
reports/demo/    可复现的示例输入与结果
portfolio/       三个已运行案例及其限制
scripts/         文档站构建、链接检查、打包
docs/            中文技术文档及官方来源
```

网页文档需要一个独立的构建依赖；分析核心不需要它：

```bash
python -m pip install -r requirements-docs.txt
python scripts/build_site.py
python scripts/check_links.py
python -m http.server 8000 --directory site
```

访问 <http://localhost:8000>。源目录 `index.html` 是入口页，构建后的 `site/` 提供 HTML 文档、搜索和结果。GitHub Actions 提供测试和 Pages 部署配置；是否已上线取决于 Pages 设置及运行结果，见 [开发与部署](docs/development.md)。

## 边界

- 已实现：合成事件、SQL 留存与收入、固定终点二元实验、SRM、带 embargo 的流失基线、离线文档站、自动检查。
- 设计文档：推荐、欺诈、生产遥测、云数仓、AI 评估。没有将这些描述为已部署系统。
- 实验仅适用于独立用户、50:50 分配、单一固定终点且成功/失败数充足的二元指标。
- 原始视频未在此版本重新取得并逐句核验；不作为视频完整转录。

## 许可与贡献

沿用原仓库声明：原创文档 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，代码和合成数据 [MIT](licenses/MIT.txt)。外部资料和商标由各自权利人持有。见 [LICENSE](LICENSE)、[贡献指南](CONTRIBUTING.md)、[变更日志](CHANGELOG.md)。
