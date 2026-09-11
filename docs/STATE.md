# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q1 FROZEN；Q2 IMPLEMENTATION & SHORT-HORIZON VALIDATION COMPLETE；Q2 LONG-HORIZON BOUNDARY & PRODUCTION CONFIG GATE COMPLETE / WAITING FOR Q2 PRODUCTION & RESULT AUTHORIZATION；Q3/Q4 未启动

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | FROZEN / COMPLETE；AUDIT COMPLETE | 温度初始 Robin 表示相容；水分初始层诊断成立；边界聚类保守 FVM + 首步 BE/随后 BDF2 完成冻结生产门；本轮独立 uniform-grid BE 审计确认 r=1.9 cm 早期 signed error 穿零，归类 cancellation dip；final workbook、图表包和官方源均未改动 | `experiments/EXP-Q1-SURFACE-DECAY/`、`experiments/EXP-003/`、`experiments/EXP-004/`、`deliverables/final/result1.xlsx` |
| Q2 | LONG-HORIZON BOUNDARY & PRODUCTION CONFIG GATE COMPLETE / WAITING PRODUCTION AUTHORIZATION | Q2-M1 长时 0–72 h、6/24/48/72 h checkpoint、被动事件观察、低含水率物性范围、Picard/守恒/Robin/重启和时间/空间收敛均已验证；主 ENV-A 原始输出因一次中断恢复产生重复行，已保留 raw 并生成逐键去重的完整 recovered artifact；未生成 `result2.xlsx`；环境尾段、PCHIP、h/hm、界面平均、终点和精度门仍待人工冻结 | `src/q2/`、`experiments/EXP-Q2-012-ENVIRONMENT/`–`EXP-Q2-020-BASELINE/`、`docs/EXPERIMENTS.md` |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design/实现/验证/全时域收敛/冻结交付/可视化；Q2 Model Design、实现、独立 benchmark、耦合/敏感性/重启、0–3 h短时验证、0–72 h长时边界/生产候选验证
- 当前主模型/主方案：Q1 M1 生产行为保持冻结；Q2-M1 固定半径一维径向变物性温度–水分耦合；Candidate A 为 clustered conservative FVM + BE startup/BDF2，`dt=.25 s`、`n=80`、linear、harmonic、ENV-A last raw point 后常值；仅为推荐候选，仍不是 FINAL
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：Q2 ENV-A 主候选完成 `259200 s`；最终阶段 `Picard=2/2/2/2`（min/median/p95/max），`C` 范围 `0.0516273–2.55 kg/kg`，`D` 最小 `2.6499e-12 m²/s`；单步质量残差 `2.34e-11`、热残差 `1.78e-10 J`；被动 `C<0.15` 首次观察 bracket 为 `205913–205913.25 s`，未触发停止。长时收敛组与已完成的短时正式 time/space order 分开登记；主输出使用完整 recovered 1 s 网格
- 正在进行的实验：NONE；Q2 长时门已完成并保留 raw/recovered 证据，Q3/Q4 未启动；Q1 `result1.xlsx` SHA-256 仍为 `06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c`，Q1 freeze reference SHA-256 仍为 `f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17`

## 风险与下一步

- 主要问题：Q1 的20–40 s近表面绝对误差深谷已证明是 signed zero-crossing/cancellation dip，不得写成算法突然提速；Q2 的 `OQ-Q2-ENV-001/002`、`OQ-Q2-BC-001`、`OQ-Q2-FVM-001`、`OQ-Q2-END-001`、`OQ-Q2-ACC-001` 仍未决
- Blockers：Q2 不能进入正式 `result2.xlsx`/最终交付，除非人工确认开放问题、终点/行数和精度门，并另行授权生产；Q3/Q4 未授权
- 实现边界兼容标记：本轮完成 Q2 long-horizon boundary & production config gate；不包含 Q2 final deliverable、不包含 Q3/Q4、不包含官方 `result2.xlsx`
- 最高优先级任务：保持 Q1 冻结资产和 `A题/` 只读；人工审阅 EXP-Q2-012–020 的环境/插值/边界/界面/终点/精度证据；不得把长时 proxy 或被动事件观察写成最终论文结论
- 推荐下一步：人工冻结 Q2 配置与交付契约后，再单独授权正式生产和 `result2.xlsx` candidate；在此前不要生成 `result2.xlsx`，不要启动 Q3/Q4

## 更新时间

- 最后更新时间：2026-09-11（Q2 long-horizon boundary & production config gate 完成；本地提交，不推送；未生成 result2，Q3/Q4 未启动）
