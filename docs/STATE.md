# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q1 FROZEN；Q2 FORMAL-OUTPUT ACCURACY GATE COMPLETE，等待 V3 freeze-run 授权；Q3/Q4 未启动

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | FROZEN / COMPLETE；AUDIT COMPLETE | 温度初始 Robin 表示相容；水分初始层诊断成立；边界聚类保守 FVM + 首步 BE/随后 BDF2 完成冻结生产门；本轮独立 uniform-grid BE 审计确认 r=1.9 cm 早期 signed error 穿零，归类 cancellation dip；final workbook、图表包和官方源均未改动 | `experiments/EXP-Q1-SURFACE-DECAY/`、`experiments/EXP-003/`、`experiments/EXP-004/`、`deliverables/final/result1.xlsx` |
| Q2 | FORMAL-OUTPUT ACCURACY GATE COMPLETE / WAITING V3 FREEZE RUN AUTHORIZATION (HISTORICAL ORIGINAL ACCURACY GATE FAILED) | n320/cluster3、early fine window through 5 s、BE restart/BDF2 的 transition integer lattice 和 early official lattice 通过；3–48 h 局部 n640、passive/final n160 定点证据通过。`14400.25 s,r=2.0 cm` 温度峰 `2.2991e-4 °C` 仅为有界 internal diagnostic，未污染正式点；未生成 `result2.xlsx` | `experiments/Q2_ACCURACY_REMEDIATION/accuracy_confirmation_v3.json` |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design/实现/验证/全时域收敛/冻结交付/可视化；Q2 Model Design、实现、独立 benchmark、耦合/敏感性/重启、formal transition/early audits、targeted long-horizon certification
- 当前主模型/主方案：Q1 M1 生产行为保持冻结；Q2-M1 固定半径一维径向变物性温度–水分耦合；推荐 `Q2_NUMERICAL_CONFIG_V3` 为 n=320/cluster3、early `dt=.015625 s` through5 s、production `dt=.25 s`、BE startup/BDF2、event-aligned BE restart、linear、harmonic、ENV-B constants；formal evidence 已通过，但结果候选仍未生成、不是 FINAL
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：formal transition T/C L∞=`1.55375452663975e-5/3.1402255240564614e-9`；early policy5 T/C L∞=`7.116765686987492e-6/1.0270424274150258e-5`；3–48 h targeted n640 reference T/C L∞=`1.2509725024756335e-6/2.987415287369899e-6`；所有候选/参考场有限，Picard、质量和热量诊断已保存。被动 bracket `[207034.5,207034.75] s` 仍仅作 horizon observer。
- 正在进行的实验：NONE；formal certification 已完成，V2 n640 full attempt 保留为 aborted provenance；等待人工授权 Q2_FREEZE_RUN_V3；Q1 `result1.xlsx` SHA-256 仍为 `06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c`，Q1 freeze reference SHA-256 仍为 `f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17`

## 风险与下一步

- 主要问题：Q1 的20–40 s近表面绝对误差深谷是 signed zero-crossing/cancellation dip；Q2 的 `14400.25 s` local probe 仍高于 formal gate，但已证明不传播到整数秒 formal output；旧 production accuracy failure 和 V2 aborted run 继续保留为历史证据
- Blockers：仅剩 Q2 V3 freeze-run 的人工授权；在授权前 candidate `result2.xlsx` 和 Q2 formal figures 继续 fail-closed，Q3/Q4 未授权
- 实现边界兼容标记：本轮完成 Q2 production freeze run 与独立精度审计；不包含 Q2 candidate/final deliverable、不包含 Q3/Q4
- 最高优先级任务：保持 Q1 冻结资产和 `A题/` 只读；等待人工授权后用新目录执行 Q2 V3 从 `t=0` 的双跑、lineage、determinism、candidate workbook 和 figures 验证；不得续跑 `Q2_FREEZE_RUN_V2`
- 推荐下一步：仅在明确授权后运行 `Q2_FREEZE_RUN_V3`；在此之前不生成 `result2.xlsx`，不生成正式 Q2 figures，不启动 Q3/Q4

## 更新时间

- 最后更新时间：2026-09-12（Q2 formal-output accuracy gate 已完成；等待 V3 freeze-run 授权；result2 未生成；本地提交，不推送；Q3/Q4 未启动）
