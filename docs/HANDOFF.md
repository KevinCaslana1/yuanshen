# Handoff

> 本文件保持很短，只服务于新会话、上下文压缩或其他 Agent 的快速接管。

## 当前做到哪里

Q1 已人工冻结并完成最终交付，Q1 signed-error 审计已确认 r=1.9 cm 的早期谷值是 `pointwise error zero-crossing / cancellation dip`，不能写成突然提速。根据新的人工授权，Q2 已完成 long-horizon boundary & production config gate：代码、测试、EXP-Q2-012 至 EXP-Q2-020 证据均已写入本地工作树；没有生成 `result2.xlsx`，没有启动 Q3/Q4。

## 当前主方案

Q2-M1：固定半径一维圆柱径向、附录3变物性、温度–水分 coupled Picard、保守变量系数 FVM。当前推荐 Candidate A 为边界聚簇网格 + BE 首步/BDF2、`n=80`、`dt=.25 s`、linear、harmonic、ENV-A last raw point 后常值；仍是 `PENDING_HUMAN_APPROVAL`，不是 FINAL；Candidate B/B0 保留为对照。

## 关键证据

- `EXP-Q2-003`：独立变量系数 benchmark，当前 Robin 节点闭合空间约一阶、BE 时间约一阶。
- `EXP-Q2-005`：固定 `dr=.025 cm`，`dt=1/.5/.25/.125 s`，reference `dt=.03125 s`；observed order 温度约 `1.047/1.099/1.222/1.585`，水分约 `0.999/1.072/1.206/1.577`。
- `EXP-Q2-006`：固定 `dt=.125 s`，`dr=.1/.05/.025 cm`，相对 `.0125 cm` reference 的温度/水分 L∞、L2 均下降。
- `EXP-Q2-010`：300 s checkpoint restart 到600 s，温度/水分末场最大差均为0。
- `EXP-Q2-011`：Candidate A、`dt=.25 s`、160 intervals、0–10800 s完成；Picard `min/median/p95/max=2/2/3/3`。
- `EXP-Q2-012`–`015`：环境尾段、linear/PCHIP、h/hm 和界面平均的独立敏感性；linear/PCHIP 不等价，arithmetic/harmonic 在当前真实运行差异很小，但均不自动冻结。
- `EXP-Q2-016`：ENV-A 0–72 h完成；最终阶段 Picard `2/2/2/2`，低含水率 `D_min=2.6499e-12 m²/s`，被动 `C<0.15` bracket 为 `205913–205913.25 s`，无事件停止。raw 追加文件重复已保留并生成完整 recovered sampler。
- `EXP-Q2-017`–`020`：长时 time/space stability proxy、ENV-A/B差异、12 h→24 h restart exact match、B0有限成本控制。

## 不要重复尝试什么

不要修改 `A题/`、Q1 solver、Q1 final 或图表；不要生成或复制 `result2.xlsx`；不要把 Q2 候选写成 FINAL；不要把 Q3 `C<0.15` 写成 Q2 终点；不要在没有新授权前启动 Q3/Q4；不要把 recovered long-horizon proxy 写成严格新阶数证明。

## 当前开放项与下一步

`OQ-Q2-ENV-001`（14400 s 后环境）、`OQ-Q2-ENV-002`（linear/PCHIP）、`OQ-Q2-BC-001`（h/hm）、`OQ-Q2-FVM-001`（算术/调和界面平均）、`OQ-Q2-END-001`（Q2终点）和 `OQ-Q2-ACC-001`（精度门）仍 OPEN。长时门已完成，当前等待人工冻结配置/终点/精度门并另行授权正式 Q2 production 与 `result2.xlsx` candidate；在此之前保持 `result2.xlsx` 不存在于 candidate/final，并保持 Q3/Q4 NOT STARTED。

## 重点阅读文件

`docs/STATE.md`、`docs/EXPERIMENTS.md`、`docs/FINDINGS.md`、`docs/FAILURES.md`、`docs/VALIDATION.md`、`experiments/EXP-Q2-016-LONG-ENV-A-last-raw/metrics.json`、`experiments/EXP-Q2-017-LONG-CONVERGENCE/metrics.json`。

## 源完整性

Q1 final SHA-256：`06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c`。Q1 freeze reference SHA-256：`f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17`。本轮只做本地提交，不推送远端。
