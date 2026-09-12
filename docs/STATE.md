# Current Project State

> 本文件只描述当前真实状态，不记录历史过程。

## 比赛与赛题

- 比赛：2026 高教社杯全国大学生数学建模竞赛；赛题：A题《药材的烘干问题》
- 官方源：`A题/`（OFFICIAL_SOURCE / IMMUTABLE_SOURCE），本轮哈希未变化
- 当前阶段：Q1 FROZEN；Q2 V3 production freeze 已完成；Q3/Q4 candidate production 已完成，等待人工冻结批准

## 各问题状态

| 问题 | 状态 | 当前结论 | 证据 |
|---|---|---|---|
| Q1 | FROZEN / COMPLETE | r=1.9 cm 早期表面绝对误差谷值由 signed error zero-crossing/cancellation dip 造成，不是精度突然提高；final result1 未改 | `experiments/EXP-Q1-SURFACE-DECAY/`、`deliverables/final/result1.xlsx` |
| Q2 | FROZEN | V3 Run1 是唯一 `PRODUCTION_CANONICAL` 生产来源；Run1/Run2 全量 raw、official sampled、diagnostics byte/hash identical；candidate 已按 byte-for-byte COPY 进入 final；工作簿和图表 final 验证 PASS | `experiments/Q2_FINAL_FREEZE/`、`deliverables/final/result2.xlsx`、`deliverables/final/figures/q2/` |
| Q3 | CANDIDATE COMPLETE | 固定半径候选首次严格低于 `0.15 kg/kg` 的局部细化时刻为 `206935.2265625 s`（`57.4820074 h`）；临界节点由数据扫描得到为 `r=0.0 cm` | `experiments/Q3_PRODUCTION/`、`deliverables/candidate/result3.xlsx`、`deliverables/candidate/paper/` |
| Q4 | CANDIDATE COMPLETE | 附录4物性 + 附件2单调PCHIP半径 + 材料坐标候选首次严格低于 `0.15 kg/kg` 的时刻为 `191097.7336094 s`（`53.0827038 h`），`R(t4)=1.2 cm`，临界材料坐标 `ξ=0` | `experiments/Q4_PRODUCTION/`、`deliverables/candidate/result4.xlsx`、`deliverables/candidate/paper/` |

## 当前 Q2 方案

- 模型：固定半径一维径向变物性温度–水分耦合 FVM；中心对称，表面 Robin，Picard 耦合；内部计算保留完整浮点精度。
- 冻结配置：n=320、cluster_power=3、harmonic interface；early `dt=0.015625 s` 至 `t=5 s`；production `dt=0.25 s`；BE startup/BDF2；5 s step change 与 `t=14400 s` 均按认证策略 BE restart；Attachment 1 在 14400 s 前线性插值，之后 ENV-B 常值 `(49.99525 °C, 0.049988 kg/kg)`。
- 生产 horizon：独立 passive bracket `[206935.0,206935.25] s`，`ceil(t_high)+21600=228536 s`；官方输出仅为整数秒 `1..228536`、21 个半径；raw 另保留 t=0 和内部诊断范围。
- 生产来源：`experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv`；哈希以 `experiments/Q2_FREEZE_RUN_V3/output_hashes.json` 为准。

## 已验证门禁

- formal-output accuracy basis：transition/early/selected long points 达到预设 `2.5e-5` 范围；不宣称 n=640 full-horizon proof。
- Run1/Run2：均从 t=0、官方初值、无旧 checkpoint/field/data 复用；Picard non-converged=0，Picard max=3；mass、heat、Robin、center symmetry、time-step residual 全部通过；确定性 PASS。
- 候选工作簿：两张表均为 `228537×22`（含表头），4 位小数、无公式；Run1 分层 trace `100/100`，Table3/4 trace `60/60`。
- 图表：FIG-Q2-01…08、FIG-Q2-V01…V03，共 11 组，PNG ≥300 dpi + SVG；30/30 trace；无 smoothing、无 numeric interpolation。
- Q1/A题 integrity、Q3/Q4 boundary 均 PASS。

## 已知失败与边界

- `Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912/`：旧 endpoint attempt，首次独立 bracket 与 carried-forward horizon 不一致，未作为来源。
- `Q2_FREEZE_RUN_V3_POSTPROCESS_FAILURE_20260912/`：Run1 数值已完成后的非数值 probe-writer 失败，部分文件仅作 provenance；未改动 solver 或 Run1 数值。
- artifact-tool 对超大工作簿两次达到 V8 heap 上限；最终按 `openpyxl write_only=True` 流式 fallback 完成并验证；final 阶段仅对已验证 candidate 执行 byte-for-byte COPY。
- Q1 的 20–40 s 误差深谷以及 Q2 的 `14400.25 s` internal diagnostic 均不得写成模型优越性或突然收敛证据。

## Q3/Q4 当前候选证据

- Q3 从冻结 Q2 raw official lattice 读取完整浮点值；粗夹逼为 `[206935,206936] s`，局部 BE/Picard `1/1024 s` 细化的首次严格低于时刻为 `206935.2265625 s`。`t=206935` 仍为 `0.1500000658293865`，`t=206936` 为 `0.14999977460230157`；端点全 21 个节点均低于阈值，critical node 为扫描结果而非预设。
- Q4 使用附录4：`rho=760+90C`、`cp=1850+2150C/(C+1)`、`k=0.12+0.20C/(C+1)`、`D=4.2e-4 exp(-0.30/C) exp(-3850/T_K)`；内部 `ξ=r/R(t)`，附件2节点 PCHIP 误差为 `0`，附件结束后保持 `R_last=1.198 cm`。粗夹逼 `[191096,191100] s`，局部细化后 `t4=191097.7336093787 s`。
- Q4 所有固定物理位置超过当前半径的单元均为空，surface 单列；生产 candidate 工作簿无公式、四位小数显示、`result3` 为 `3450×22`，`result4` 为 `3186×22`。质量守恒诊断最大归一化逐步残差 `3.4553928505477293e-4`，Robin 独立通量差最大 `4.5474756348265686e-7`，均已保留在 validation 证据中。
- 统一候选交付状态：`Q1 = FROZEN`、`Q2 = FROZEN`、`Q3 = CANDIDATE COMPLETE`、`Q4 = CANDIDATE COMPLETE`、`WAITING FOR HUMAN Q3/Q4 FREEZE APPROVAL`。本轮不写 `deliverables/final/result3.xlsx`/`result4.xlsx`，不启动 Q3/Q4 之后工作，不 push。

## 交接

- 当前最高优先级：保持 Q1/Q2 冻结交付可审计，等待人工审查 Q3/Q4 candidate；未经新授权不得将 Q3/Q4 candidate 复制到 final。
- 本地提交，按用户要求不推送远程。
- 更新时间：2026-09-12。
