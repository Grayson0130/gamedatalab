# 推荐系统（Game Recommendation）

## 流程

搜索相关项 + 排序。

## 方法

- 协同过滤（Collaborative Filtering）：
  - Item-based：基于物品相似度；计算量更小，应用更广。
  - User-based：找到相似用户；计算量大。
- 基于内容（Content-based）、基于用户行为、深度学习。
- 图推荐（Graph-based）：节点+边表征游戏生态；Graph Database（Neo4j、JanusGraph）。

## 2026 更新

- 深度学习/Transformer 多模态推荐；LLM 用于语义理解与自然语言推荐。
- 实时推荐与在线学习（bandits、强化学习）。
- 隐私与冷启动：更多依赖内容特征与上下文。
EOF