# 埋点、事件契约与质量

遥测应服务具体决策，避免先收集全部点击再寻找用途。本仓库是本地合成事件演示，不是生产 SDK。

## 生产契约建议

每条事件至少标明 `event_id`、`event_name`、`schema_version`、`event_time`、`ingestion_time`、`user_id`、`session_id`、`platform`、`app_version`、`locale`、`consent_state`。身份与同意记录按业务和地区设计；本仓库的日级简化契约见 [data/README.md](../data/README.md)。

| 事件 | 触发 | 建议参数 | 权威来源 |
| --- | --- | --- | --- |
| session_start | 有效启动/会话边界 | session_id、版本、语言 | 客户端与服务端对账 |
| tutorial_step | 步骤进入/完成 | step_id、结果、耗时 | 游戏逻辑 |
| level_end | 关卡结束 | level_id、结果、尝试次数 | 可行时服务端 |
| purchase_verified | 验单成功 | order_id、币种、金额 | 服务端订单账本 |
| refund | 退款确认 | original_order_id、金额、时间 | 商店/支付账本 |
| experiment_exposure | 实际接触处理 | experiment_id、variant、配置版本 | 分流/暴露服务 |
| localization_issue | 人工或规则发现问题 | text_key、locale、build、严重度 | 经复核的 LQA 工具 |

不要在日志记录明文邮箱、完整聊天或支付凭证；文本截图与崩溃日志也可能包含个人数据。

## 交付语义

- 重试复用同一 event_id。完全相同的重复可幂等去重，同 ID 不同负载应隔离报警，不能默默取第一条。
- 服务端设置允许的时钟偏移；迟到事件按事件时间回补，保留摄取时间评估延迟。
- 订单 ID 的业务去重独立于事件 ID；交易重试不能制造多笔收入。
- 字段改义或删除视为破坏性变更；双写迁移、版本兼容与回填需有明确计划。

## Unity 接入的版本差异

官方当前指引区分 Unity 6.2+ / Analytics SDK 6.1+ 与更早版本：较新组合通过 Developer Data framework 的 consent state 控制采集，旧组合使用相应 Analytics 采集 API。不能将旧版初始化片段当跨版本模板；删除数据也有同意状态前置条件。[S4](sources.md)

此处不粘贴未经目标项目编译的 C# SDK 示例。实际集成需锁定引擎、包版本，先定义事件及字段，再在测试环境验证同意、拒绝、撤回、离线重试和数据删除。

## 数据验收与运行手册

启动前检查 schema/type、空值、ID 唯一性、外键、金额符号与时间先后。运行中比较每平台/版本事件到达量、延迟分位数、去重比例和订单账本总额。任何异常先冻结受影响报表，定位上线时间和受众，回放隔离数据后再恢复指标。

SLA 应以业务要求设定，例如日报截止后是否允许回补、修订后如何通知使用者；本文不将任意延迟阈值写成行业标准。

关联：[指标](metrics.md) · [治理](governance.md)
