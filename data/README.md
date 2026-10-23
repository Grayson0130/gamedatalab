# 教学数据契约

所有 CSV 均由 `gamedatalab/synthetic.py` 确定性生成，无真实个人信息、外部数据集或 API。默认种子 42，截止 2026-09-30，安装日覆盖 2026-07-01 到 2026-09-13。单位 USD cents；日期为 UTC 日历日。

| 文件 | 粒度/主键 | 字段 |
| --- | --- | --- |
| users.csv | 每合成玩家一行；user_id | install_date、channel、variant |
| events.csv | 每事件一行；event_id | user_id、event_date、event_name、revenue_cents |
| acquisition_costs.csv | 每玩家一行；user_id | cost_cents |
| retention.csv | 安装日×day_n | cohort_size、retained、retention；未成熟为空 |
| summary.json | 一次分析 | 种子、规模、窗口、LTV、实验、流失指标 |
| input-hashes.json | 每输入文件 | SHA-256 |

事件类型：session、tutorial_complete 金额为零；purchase 正数；refund 负数。用户外键、金额符号与非负成本由 SQLite 约束；代码检查 ISO 日期、安装先后、成本覆盖和冲突事件 ID。完全一致的重试可去重。

## 生成机制与偏差

每玩家抽取一个潜在参与倾向，日活概率随年龄衰减；D0 总有 session。活动日按固定概率交易，订单值从几个离散金额抽取；部分订单同日退款。所有人随机分入 control/treatment，treatment 的教程完成概率被人为加 0.035。

因此不能从示例「发现」真实行业规律或证明文案有效。简化模型没有社交图、跨端身份、赛季、地区、时区、作弊、广告收入、延迟支付、用户同意和收入会计。渠道只是合成标签，不推导真实归因因果关系。

大规模参数会增加内存，生成器将事件保存在列表，适合学习而非生产流处理。更换真实数据应实现单独适配器，不伪装成这个生成器的结果。

本目录不重复存 CSV，见 [已生成输入](../reports/demo/users.csv)。结构定义：[schema.sql](../sql/schema.sql)。
