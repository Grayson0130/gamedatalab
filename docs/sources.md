# 官方来源与核对范围

访问/核对日期：**2026-10-23**。下列链接为一手资料；原文版权归各机构。本仓库只作有限摘要，核心代码与教学案例为独立编写。动态文档可能不显示发布日期，不能把访问日期误写成发布日期。

| ID | 来源 | 日期/状态 | 支持的范围 |
| --- | --- | --- | --- |
| S1 | [Google Privacy Sandbox feature status](https://privacysandbox.google.com/overview/status) | 页面标注 2026-08-14 更新 | Chrome/Android 广告 API 与其他隐私能力的不同状态 |
| S2 | [Apple AdAttributionKit updates](https://developer.apple.com/documentation/updates/adattributionkit) · [WWDC25 What’s new](https://developer.apple.com/videos/play/wwdc2025/221/) | 更新记录含 June 2025；截至核查日 | AAK 再参与能力与版本核查入口；不证明所有网络已支持 |
| S3 | [Unity 2026 report](https://unity.com/resources/gaming-report) · [官方解读](https://unity.com/blog/2026-unity-game-development-report-trends) | 解读 2026-03-09 | 受访开发者与厂商生态观察，不代表全行业普查 |
| S4 | [Unity Analytics get started](https://docs.unity.com/en-us/analytics/get-started/get-started) · [Events](https://docs.unity.com/en-us/analytics/events/events) | 动态版本文档 | 初始化、同意、版本差异和标准/自定义事件 |
| S5 | [Microsoft PlayFab experiments](https://learn.microsoft.com/en-us/xbox/playfab/live-service-management/game-configuration/experiments/experimentation-keys) · [Microsoft SRM research](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/) | 持续维护文档与研究 | 分组比例不匹配的定义及调查原则 |
| S6 | [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) · [Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) | 动态 stable 文档 | 数据泄漏、训练/测试隔离、时间相关数据的切分 |
| S7 | [DuckDB 1.5 release](https://duckdb.org/2026/03/09/announcing-duckdb-150) · [Python overview](https://duckdb.org/docs/stable/clients/python/overview) | 发布 2026-03-09 | 本地分析能力与该版本发布；未强制采用该版本 |
| S8 | [FTC COPPA final amendments](https://www.ftc.gov/legal-library/browse/federal-register-notices/16-cfr-part-312-coppa-final-rule-amendments) · [Federal Register 原文](https://www.govinfo.gov/content/pkg/FR-2025-04-22/html/2025-05904.htm) | 公布 2025-04-22；生效 2025-06-23；多数条款合规 2026-04-22 | 美国 COPPA 修订时间点，特定条款有例外 |
| S9 | [Steamworks Content Survey](https://partner.steamgames.com/doc/gettingstarted/contentsurvey?l=english) | 当前动态问卷 | AI 内容范围、预生成/实时生成披露与 guardrails |
| S10 | [actions/checkout](https://github.com/actions/checkout) · [actions/setup-python](https://github.com/actions/setup-python) | 当前 README 与 v7 远程标签 | CI 使用的 action 主版本；Pages actions 见各官方仓库 |

## 证据限制

Apple 主文档使用动态渲染，研究时正文读取有限；AAK 能力依据官方搜索摘要与更新记录，部署前应在目标 OS/SDK 环境核验。没有据此编造 2026 WWDC 的新增 API。

本次未引入实时招聘、市场规模、平均 CPI、各商店现行佣金或特定地区薪酬数据。这些内容变动快且口径差异大，不能用教学合成数据填充。推荐、欺诈、数据栈取舍是设计建议，尚无生产实测。

## 更新步骤

优先查机构原页与发布说明，检查时间和适用版本，保留变化摘要。遇到摘要与正文冲突以正文为准；无法核实则降级为待核实项，不补写看似合理的数字。提交中应同时更新日期与受影响文档。
