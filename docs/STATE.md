# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。每次重要工作阶段结束时更新，并保持简短。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛
- 赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE）
- 当前阶段：Q1 FROZEN；Q2 PRODUCTION CONFIG FROZEN 但 ACCURACY GATE FAILED / RESULT CANDIDATE BLOCKED；Q3/Q4 未启动

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | FROZEN / COMPLETE；AUDIT COMPLETE | 温度初始 Robin 表示相容；水分初始层诊断成立；边界聚类保守 FVM + 首步 BE/随后 BDF2 完成冻结生产门；本轮独立 uniform-grid BE 审计确认 r=1.9 cm 早期 signed error 穿零，归类 cancellation dip；final workbook、图表包和官方源均未改动 | `experiments/EXP-Q1-SURFACE-DECAY/`、`experiments/EXP-003/`、`experiments/EXP-004/`、`deliverables/final/result1.xlsx` |
| Q2 | PRODUCTION CONFIG FROZEN / ACCURACY GATE FAILED / RESULT CANDIDATE BLOCKED | 批准的 Candidate A production Run1/Run2 均从 `t=0` 到 `228635 s` 完成且 raw/sampled/diagnostics/checkpoint 完全确定；但独立 dt=.125/n=160 reference 的 T/C L∞ 分别为 `1.9082e-4/2.0357e-4`，超过内部 `2.5e-5` gate；未生成 `result2.xlsx` 或 Q2 figures | `docs/Q2_PRODUCTION_FREEZE.md`、`docs/Q2_RESULT_AUDIT.md`、`experiments/Q2_FREEZE_RUN/` |
| Q3 | NOT STARTED | 尚未建立模型 | — |
| Q4 | NOT STARTED | 尚未建立模型 | — |

## 当前方案

- 已完成：官方题目与资产登记、Q1-Q4 注册、输入与模板校验基础设施、Q1 Model Design/实现/验证/全时域收敛/冻结交付/可视化；Q2 Model Design、实现、独立 benchmark、耦合/敏感性/重启、0–3 h短时验证、0–72 h长时边界/生产候选验证
- 当前主模型/主方案：Q1 M1 生产行为保持冻结；Q2-M1 固定半径一维径向变物性温度–水分耦合；批准的 production 配置为 Candidate A clustered conservative FVM + BE startup/BDF2，`dt=.25 s`、实际98 cells、linear、harmonic、post-14400 常值 `49.99525 °C/0.049988 kg/kg`；配置已冻结，但结果候选未通过精度门，不是 FINAL
- Baseline：B0；M2 常-D径向模型和 M3 Dirichlet 模型已完成对照
- 当前最好结果：Q2 freeze Run1/Run2 完成 `228635 s`；Picard=`2/2/3/3`（min/median/p95/max），`C` 范围 `0.0522058–2.55 kg/kg`，`D` 最小 `2.9004e-12 m²/s`；质量残差最大 `1.5712e-8`、离散热残差最大 `1.2149 J`；被动 bracket `[207034.5,207034.75] s` 仅作 horizon observer。精度确认失败：T/C L∞=`1.9082e-4/2.0357e-4`；未生成 candidate。
- 正在进行的实验：NONE；Q2 production/reference 已完成但 accuracy gate FAIL，Q2 candidate blocked，Q3/Q4 未启动；Q1 `result1.xlsx` SHA-256 仍为 `06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c`，Q1 freeze reference SHA-256 仍为 `f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17`

## 风险与下一步

- 主要问题：Q1 的20–40 s近表面绝对误差深谷是 signed zero-crossing/cancellation dip；Q2 已批准配置在 `14400 s` 环境跳变和 `t=1 s` 初始表面层处产生超门误差
- Blockers：Q2 accuracy gate FAIL，candidate `result2.xlsx` 和 Q2 figures 被 fail-closed 阻止；若要改变 post-14400 规则、网格/时间步或内部门，需新的人工决定；Q3/Q4 未授权
- 实现边界兼容标记：本轮完成 Q2 production freeze run 与独立精度审计；不包含 Q2 candidate/final deliverable、不包含 Q3/Q4
- 最高优先级任务：保持 Q1 冻结资产和 `A题/` 只读；人工审阅 `docs/Q2_RESULT_AUDIT.md`，决定是否授权精度整改；不得把 production failure 写成模型优越性或 Q3 结论
- 推荐下一步：等待人工决定精度整改方向；在新授权前不重跑 production、不生成 `result2.xlsx`、不启动 Q3/Q4

## 更新时间

- 最后更新时间：2026-09-12（Q2 production freeze 双跑完成但 accuracy gate FAIL；candidate blocked；本地提交，不推送；Q3/Q4 未启动）
