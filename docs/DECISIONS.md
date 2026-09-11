# Decisions

这里记录真正影响后续建模、实验或论文的决策，不记录普通偏好或临时调试。

## 决策索引

| ID | 日期 | 问题 | 决策 | 状态 | 证据 |
|---|---|---|---|---|---|
| D-Q1-001 | 2026-09-10 | Q1 | M1（一维径向非线性扩散 + Robin 边界）获人工冻结批准；B0 作为 Baseline，M2/M3 作为对照 | APPROVED_FROZEN | `docs/DECISIONS.md`、`docs/Q1_FINAL_FREEZE_AUDIT.md` |
| D-Q1-NUMGRID | 2026-09-11 | Q1 | 历史敏感性使用均匀 `N=40/80/160`；生产网格由 Q1 freeze 决策单独规定 | SUPERSEDED_FOR_PRODUCTION | `docs/Q1_PLAN.md`、`docs/DECISIONS.md` |
| D-Q1-HM | 2026-09-11 | Q1 | 在实现候选中按团队建模口径令 `hm` 直接作用于干基浓度 `C`，不乘空气密度；保留为建模假设并做 M3 对照 | ACCEPTED_MODELING_ASSUMPTION | `docs/Q1_PLAN.md`、OQ-006 |
| D-Q1-M2 | 2026-09-11 | Q1 | M2 对照模型固定 `D=D(C_ref)`，默认 `C_ref=2.55 kg/kg` 初始干基含水率；不替代 M1 | ACTIVE | `src/q1/solver.py`、EXP-002 |
| D-Q1-OQ005 | 2026-09-11 | Q1 | `result1.xlsx` A列采用 `1,2,...,1800 s`，不写 `t=0` 行；这是团队交付约定，不是官方事实 | ACCEPTED_TEAM_DELIVERABLE_DECISION | 本轮人工授权、`docs/DELIVERABLE_SPEC.md` |
| D-Q1-OQ006 | 2026-09-11 | Q1 | `hm` 直接作用于干基浓度 `C`，不乘空气密度、材料密度或其他未给因子 | ACCEPTED_MODELING_ASSUMPTION | 本轮人工授权、EXP-005、EXP-007 |
| D-Q1-OQ007 | 2026-09-11 | Q1 | 中心与表面采用内部 solver 节点值；最终网格必须严格对齐 `0.0,0.1,...,2.0 cm` | ACCEPTED_NUMERICAL_DECISION | 本轮人工授权、`D-Q1-NUMGRID` |
| D-Q1-OQ008 | 2026-09-11 | Q1 | 不加入潜热、内部蒸发源项、Soret/Dufour 或其他需要新增未知参数的耦合项 | ACCEPTED_MODELING_SIMPLIFICATION | 本轮人工授权、EXP-007 |
| D-Q1-FREEZE-CANDIDATE | 2026-09-11 | Q1 | 冻结验证对象为 M1；B0/M2/M3 只作验证与敏感性证据；最终配置满足 D-Q1-NUM-ACCURACY-CRITERION，舍入一致性仅作辅助 | APPROVED_FROZEN | `experiments/EXP-Q1-FULL-SPATIAL/`、`experiments/EXP-Q1-FULL-TEMPORAL/`、`experiments/Q1_FREEZE_RUN/` |
| D-Q1-NUM-T2 | 2026-09-11 | Q1 | 将“BE 首步+BDF2”作为数值整改候选进行验证，不自动替换 M1/BE 主方案；论文点改善但完整网格安全裕量不足 | CANDIDATE_NOT_FROZEN | `experiments/EXP-Q1-NUM-BENCH/`、`experiments/EXP-Q1-NUM-REMEDIATION/` |
| D-Q1-INITIAL-LAYER | 2026-09-11 | Q1 | 支持初始水分场与表面 Robin 条件形成短时边界层的数值诊断；保持官方初值/边界不变，边界聚类已通过全时域验证 | DIAGNOSTIC_SUPPORTED_PRODUCTION_FROZEN | `docs/Q1_INITIAL_LAYER_AUDIT.md`、`experiments/EXP-Q1-FULL-SPATIAL/`、`experiments/Q1_FREEZE_RUN/` |
| D-Q1-NUM-ACCURACY-CRITERION | 2026-09-11 | Q1 | 将 estimated discretization uncertainty 作为主要内部数值门：温度和含水率均要求 `<5e-5`（各自输出单位）；四舍五入状态只作辅助证据，不因少量 ambiguous 自动失败 | TEAM_NUMERICAL_CRITERION | 本轮人工授权、后续全时域收敛实验 |
| D-Q1-HUMAN-FREEZE | 2026-09-11 | Q1 | 人工批准 Q1 M1、生产网格、时间积分、候选到 final 的字节复制、最终验证和可视化交付；代码冻结基线与审计文档提交保持分离 | APPROVED | `docs/Q1_FINAL_FREEZE_AUDIT.md`、`deliverables/final/Q1_MANIFEST.json` |
| D-Q2-001 | 2026-09-11 | Q2 | 将 Q2-M1 设计为固定半径一维圆柱径向、附录3变物性、温度–水分双场耦合的主候选；仅登记设计，不代表实现或冻结 | DESIGN_CANDIDATE_NOT_IMPLEMENTED | `docs/Q2_PLAN.md`、官方 PDF 附录3 |
| D-Q2-NUM-CANDIDATES | 2026-09-11 | Q2 | 保留 Q1 聚簇保守 FVM + BE/BDF2 的 Candidate A 与 uniform FVM + BE 的 Candidate B；Candidate C 仅在 A/B 诊断失败时启用 | PENDING_IMPLEMENTATION_AUTHORIZATION | `docs/Q2_PLAN.md` |
| D-Q2-COUPLING | 2026-09-11 | Q2 | 采用 block Gauss–Seidel / coupled Picard 的实现设计：先 T、后 C、分别归一化残差、最大迭代与 fail-closed 日志 | DESIGN_ONLY | `docs/Q2_PLAN.md` |
| D-Q2-ENV-001 | 2026-09-11 | Q2 | 附件1尾段和 `14400 s` 后环境常值尚未决定；`50.00°C/0.0500` 仅为 TEAM_REFERENCE 建议 | OPEN | `experiments/EXP-Q2-ENV-TAIL/metrics.json`、`docs/Q2_PLAN.md` |
| D-Q2-ENV-002 | 2026-09-11 | Q2 | 分段线性与 PCHIP 均保留为环境插值候选，必须穿过官方原始点；尚未选择 | OPEN | `docs/Q2_PLAN.md` |
| D-Q2-BC-001 | 2026-09-11 | Q2 | Q1 `h/hm` 与 Robin 口径可作为延续候选，但需 Q2 人工确认和 ±10% 敏感性 | OPEN_MODELING_ASSUMPTION | `docs/Q2_PLAN.md`、`docs/ASSUMPTIONS.md` |
| D-Q2-FVM-001 | 2026-09-11 | Q2 | 变系数 FVM 的算术/调和界面平均不在设计 Gate 预先裁决 | OPEN_NUMERICAL_DECISION | `docs/Q2_PLAN.md` |
| D-Q2-END-001 | 2026-09-11 | Q2 | 不把 Q3 的 `C<0.15 kg/kg` 自动写成 Q2 官方终点；Q2 长时覆盖范围和最终行数待确认 | OPEN_INTERPRETATION | `docs/Q2_PLAN.md`、`docs/PROBLEM_SPEC.md` |
| D-Q2-ACC-001 | 2026-09-11 | Q2 | Q1 `<5e-5` 只作为 Q2 精度候选起点；需重新检查长时累积误差、事件时刻、耦合误差和运行成本 | OPEN_TEAM_CRITERION | `docs/Q2_PLAN.md` |

## D-Q1-HUMAN-FREEZE Q1 人工最终冻结与可视化交付

日期：2026-09-11
问题：Q1

### 背景

Q1 全时域空间/时间收敛和 `Q1_FREEZE_RUN` 双跑均已通过。人工授权明确批准冻结 Q1，并要求完成 candidate-to-final 交付、最终校验、图表生成和交接；该批准不扩大到 Q2/Q3/Q4。

### 最终决策

批准并冻结 M1 及其生产配置：边界聚簇保守径向 FVM（`cluster_power=2`，base320 请求网格，实际 338 个区间、339 个节点），首步 BE 后固定步长 BDF2，`dt=0.25 s`，时间范围 `0..1800 s`，官方输出位置 `0..2 cm`、间隔 `0.1 cm`。允许将已验证 candidate 原样复制到 final，并生成仅消费冻结源的 Q1 图表包。

### 证据与完整性

- 冻结运行源 SHA-256：`f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17`。
- candidate/final `result1.xlsx` SHA-256：`06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c`，字节级一致。
- 温度/含水率最大估计不确定度：`1.4012174801763968e-06 °C` / `2.7414224748183296e-05 kg/kg`，均 `<5e-5`。
- 最终工作簿校验、70 个论文点追踪、9 张图表和 20 个随机图表数据点均 PASS。
- 详见 `docs/Q1_FINAL_FREEZE_AUDIT.md`、`deliverables/final/Q1_MANIFEST.json` 和 `figures/q1/FIGURE_MANIFEST.json`。

### 状态

APPROVED

## 决策记录模板

```markdown
## D-xxx 标题

日期：YYYY-MM-DD
问题：Q1/Q2/Q3/Q4/全局

### 背景

### 候选方案

-

### 最终决定

### 原因

### 支持证据

- EXP-xxx
- FIND-xxx

### 被否决方案

### 重新评估条件

### 状态

ACTIVE / SUPERSEDED / PENDING_CONFIRMATION
```

## D-Q1-001 Q1 模型设计候选

日期：2026-09-10

问题：Q1

### 背景

Q1要求输出圆柱药材内部的温度与水分浓度空间分布，而官方只提供初始几何、Q1物性参数和烘房边界输入。当前记录涵盖实现和内部数值验证，但不把推荐候选当作已经冻结的最终模型。

### 候选方案

- B0：空间均匀的 lumped exchange Baseline。
- M1：一维径向、轴对称、`D(C)` 非线性扩散，Robin 换热/传质边界。
- M2：一维径向、常 `D` 对照模型。
- M3：Dirichlet 表面边界敏感性模型。
- M4：二维轴对称模型，仅作风险对象，因端面边界数据不足暂不实现。

### 最终决定

冻结主模型为 M1；B0 保留作 Baseline，M2/M3 保留为对照实验。

### 原因

M1 能表达题面要求的径向输出，并使用附录2给出的 `h、hm` 与 `D(C)`；其复杂度仍低于二维模型，且可用保守离散和边界通量检查验证。

### 支持证据

- 官方题面第1页、第3页和附录2。
- `docs/Q1_PLAN.md` 的 Q1 Requirement Matrix、数据审计和候选模型比较。
- EXP-001–EXP-007 已按序完成；详细配置、指标、验证状态和运行时间见 `experiments/EXP-001/`–`EXP-007/`。

### 被否决方案

当前没有永久否决；M3仅被限定为敏感性对照，M4因边界数据不足暂不作为 Q1 默认实现。实验通过只表示实现与数值检查完成，不表示最终模型已经冻结。

### 重新评估条件

smoke test、时间/空间敏感性、Baseline/M2/M3 对比、全时域收敛、冻结双跑和 final 验证均已完成；OQ-005/OQ-006/OQ-007/OQ-008 已登记解决，人工 freeze approval 已于 2026-09-11 获得。

### 状态

APPROVED_FROZEN

## D-Q1-FREEZE-CANDIDATE Q1 结果交付冻结对象

日期：2026-09-11

问题：Q1

### 背景

人工授权要求在生成 `result1.xlsx` 前，对完整交付网格和论文展示点执行原始值误差及估计离散不确定度检查；四位小数一致性仅作辅助诊断。

### 最终决定

只验证 M1 作为冻结对象；B0、M2、M3 仅作为 Baseline、消融和敏感性证据。冻结配置已通过完整 `1..1800 s × 0.0..2.0 cm` 网格和论文 7×5 点的估计离散不确定度标准；四位小数舍入差异作为辅助证据。

### 结果

`EXP-Q1-FINAL-CONV` 的旧四舍五入差异已证明原配置需要进一步审查，但不再单独作为自动失败判据。新的全时域验证完成 3 层空间和 3 层 BDF2 时间比较；最低成本通过配置为边界聚簇 base320（实际 338 个区间）、`dt=0.25 s`。温度最大估计不确定度 `1.4012e-6 °C`，含水率最大估计不确定度 `2.7414e-5 kg/kg`，均满足 `<5e-5`。

### 重新评估条件

人工已确认 Q1 冻结配置和 candidate，按 COPY ONLY 将 candidate 复制到 final；candidate/final SHA-256 完全一致。不得修改已接受的交付契约或物理模型。主要数值门按 `D-Q1-NUM-ACCURACY-CRITERION`，舍入状态保留为辅助信息。

### 状态

APPROVED_FROZEN

## D-Q1-NUM-T2 BDF2 时间积分整改候选

日期：2026-09-11

问题：Q1

### 背景

Q1 的真实运行诊断显示 BE 时间误差在完整网格上明显大于空间温度误差，且含水率误差集中在早期和表面。人工授权要求在需要时评估 BDF2 候选，同时不得未经证据把数值方法升级为最终主方案。

### 候选方案

- 保留 M1 的 Backward Euler（现有参考）。
- 一阶 BE 启动一步，随后使用 BDF2，保持相同径向 FVM、Robin 边界、物性、输入插值和 Picard 过程（M1-NUM-T2）。

### 当前决定

只将 M1-NUM-T2 登记为可复核候选，不改变物理模型。旧 `N=320`、`dt=0.5→0.25 s` 证据曾未通过完整网格安全门；在保持同一方程的边界聚簇实现和全时域复验后，生产配置已按新的团队数值标准冻结，不能把旧失败证据误写为当前冻结配置失败。

### 支持证据

- `EXP-Q1-NUM-BENCH`：独立制造解支持 BE 一阶时间阶，并为 BDF2 提供二阶候选的首个细化证据。
- `EXP-Q1-NUM-REMEDIATION`：BDF2 与 BE 的完整网格、论文点、Picard、运行时间和阈值距离比较。

### 重新评估条件

完成针对早期时间/表面含水率误差的最小附加诊断，并重新通过完整网格 Level 1–3、守恒/范围和四舍五入安全裕量；在此之前不得把候选写入交付文件。

### 状态

CANDIDATE_NOT_FROZEN

## D-Q1-M2 常扩散系数对照口径

日期：2026-09-11

问题：Q1

### 背景

需要区分 `D(C)` 非线性本身对结果的影响，同时保持与 M1 相同的径向网格、时间离散、物性参数和 Robin 边界。

### 最终决定

M2 固定 `D=D(C_ref)`，默认取配置中的初始干基含水率 `C_ref=2.55 kg/kg`；温度场仍采用与 M1 相同的常物性方程。M2 只作为消融和稳定性对照，不是最终主模型。

### 支持证据

- `src/q1/solver.py` 的 `run_m2`。
- EXP-002 中 M1/M2 的同配置对照；两者运行验证均为 PASS。

### 重新评估条件

若后续人工确认更合适的 `C_ref`，或 EXP-002 的对照目标发生变化，应重新登记该选择并重跑对照。

### 状态

ACTIVE

## D-Q1-NUMGRID Q1 内部网格与输出网格分离

日期：2026-09-11

问题：Q1

### 背景

当前 Q1 设计曾把 `0.1 cm` 输出间隔写成内部网格候选；团队资料明确建议内部 `Δr=0.25 mm, N=80`，并用更粗/更细网格做收敛比较。

### 候选方案

- 直接使用 `Δr=0.1 cm` 作为内部求解网格。
- 使用 `Δr=0.25 mm, N=80` 作为主计算网格，并采用 `N=40/80/160` 做网格敏感性。

### 最终决定

主计算网格为 `N=80, Δr=0.00025 m`。官方输出网格为 `0.001 m`，通过内部节点 `j=0,4,...,80` 直接抽取；内部网格和输出网格在代码中分别表示。

### 原因

更细内部网格降低径向离散误差，同时输出位置恰好与每四个内部节点对齐，不引入额外插值误差。该选择属于 `NUMERICAL_CHOICE`，不是官方题面事实。

### 支持证据

- 团队参考资料《问题一解决步骤》《模型与数值方案总览》。
- 官方题面只规定输出每隔 0.1 cm，并未规定内部求解网格。

### 被否决方案

`Δr=0.1 cm` 不再作为主内部计算网格；仍可作为误差对照，但不与主方案并列为默认值。

### 重新评估条件

EXP-004 的 `N=40/80/160` 结果若不能收敛，重新审查网格、中心离散、Robin 表面离散和时间步长。

### 状态

ACTIVE

## D-Q1-HM 干基浓度 Robin 边界口径

日期：2026-09-11

问题：Q1

### 背景

官方附录2给出 `hm` 的单位为 m/s 和水分浓度 `C` 的单位为 kg/kg，但未用完整文字规定 `hm` 在干基浓度边界中的具体组合方式。团队资料给出直接作用于 `C` 的口径。

### 候选方案

- 直接使用 `-D∂C/∂r=hm(C_s-C∞)`。
- 额外引入空气密度或其他未给定因子。

### 最终决定

实现候选采用第一种方案；它被记录为 `TEAM MODELING INTERPRETATION` 和 `PARTIAL / MODELING ASSUMPTION`，不是官方事实，不额外乘空气密度。

### 原因

`D∂C/∂r` 与 `hm(C_s-C∞)` 量纲一致；`C_s>C∞` 时外向通量为正；高 `hm` 极限趋向表面浓度接近外部浓度。额外密度因子没有官方参数依据。

### 支持证据

- 官方附录2的 `hm` 单位和 `D(C)` 关系。
- 团队参考资料的明确口径。
- Q1 实现前的量纲、符号和极限审查。

### 被否决方案

不采用未经官方或实验支持的空气密度乘因子。

### 重新评估条件

EXP-005 的 Robin/Dirichlet 对照、EXP-007 的通量与守恒检查若显示边界解释不可接受，或人工确认官方另有含义，则重新打开 OQ-006。

### 状态

ACCEPTED_MODELING_ASSUMPTION

## D-Q1-INITIAL-LAYER Q1 初始表面层诊断与聚类候选边界

日期：2026-09-11

问题：Q1

### 背景

完整网格诊断将含水率误差定位到早期表面；人工授权要求优先检查 t=0 相容性、扩散尺度、启动策略和边界聚类候选，不得通过修改官方初始条件或 Robin 物理口径来消除误差。

### 决定

1. 将 `H-Q1-INITIAL-LAYER` 标记为 `SUPPORTED`，其含义限于数值诊断：当前数值困难主要由初始水分场与表面 Robin 条件不相容产生的短时表面边界层导致。
2. 保持官方初始水分场、附件1和 Robin 边界不变；不将诊断结果表述为模型错误。
3. 保留均匀 M1/BE 作为可追溯参考，并把 `p=2` 的边界聚类保守 FVM 登记为数值候选。聚类候选必须显式保留全部官方输出节点，尚未冻结为生产主方案。
4. 标准 BE 首步+BDF2 继续作为既有候选；早期 BE 子步没有显示出稳定改善，不直接升级为生产策略。

### 支持证据

- `EXP-Q1-INITIAL-LAYER`：温度残差 `-0.0 W/m²`，水分残差 `-2.024296e-6 m/s`。
- `EXP-Q1-SURFACE-DECAY`：均匀网格表面误差从 t=1 到 t=100 s 显著衰减，后期阶数恢复。
- `EXP-Q1-CLUSTER-BENCH` 与 `EXP-Q1-CLUSTER-SHORT`：聚类 FVM benchmark 正常，真实 Q1 早期表面差异下降。
- `EXP-Q1-CLUSTER-TEMPORAL`：t=1 表面时间剩余约 `3.1850e-5 kg/kg`，20/21 个官方位置可舍入认证，表面仍歧义。

### 未决事项

聚类候选已完成 0–1800 s 全网格 raw、Richardson、守恒/范围、初始层和舍入辅助复验；`Q1_FREEZE_RUN` 双跑确定性通过，并生成候选副本。仍需人工确认后才允许进入 final。

### 状态

DIAGNOSTIC_SUPPORTED_PRODUCTION_FROZEN

## D-Q1-NUM-ACCURACY-CRITERION Q1 全时域内部数值精度标准

日期：2026-09-11

问题：Q1

### 背景

题面只要求最终结果保留四位小数；此前将全部 37,800 个输出单元格跨离散配置后四舍五入完全一致作为唯一阻塞判据，混淆了输出格式与数值误差。

### 决定

- `OUTPUT FORMAT`：最终 candidate 显示/写入四位小数，这是交付格式要求。
- `NUMERICAL ACCURACY`：采用 `estimated discretization uncertainty` 作为团队内部主要数值门，不是官方题面事实。
- `TEAM_NUMERICAL_CRITERION`：温度自身单位的估计离散不确定度 `<5e-5 °C`；含水率自身单位的估计离散不确定度 `<5e-5 kg/kg`。
- `ROUNDING CERTIFICATION`：逐点保存 raw value、estimated uncertainty、距最近舍入边界距离和 rounding status，仅作辅助证据；少量 `ROUNDING_AMBIGUOUS` 不自动导致数值 Gate 失败。
- 局部 Richardson 阶数若为非正或处于病态区间 `[0,0.5)` / `(4,+∞)`，不使用发散的局部外推；改用相邻粗/中/细三层中的最大原始差值作为 `RAW_ADJACENT_FINE_ENVELOPE`，并在指标中保留阶数、原始差值和方法标记。`<5e-5` 门槛不变。

### 原因

四位小数是报告分辨率，不等价于所有不同离散配置必须产生完全相同的最后一位。若 `u±ε` 的不确定度已满足内部标准，但 `u` 接近舍入边界，仍可能出现 `ROUNDING_AMBIGUOUS`；此时必须如实记录并使用冻结最高可信 raw 数值按标准四舍五入，禁止人工挑选末位。

### 支持证据

- 本轮人工授权的 Full-Horizon Production Config Freeze 提示词。
- `EXP-Q1-CLUSTER-TEMPORAL` 已展示逐官方位置保存 raw、不确定度、边界距离和舍入状态的结构。
- `docs/DELIVERABLE_SPEC.md` 的四位小数输出契约。

### 被否决方案

不再使用 `rounded disagreement count > 0 => 自动 FAIL`。在没有新的证据前，不额外加入未经依据的 safety factor，也不因追求 `ROUNDING_AMBIGUOUS=0` 无限加密网格或减小时间步。局部 Richardson 病态时也不使用无界外推值，而使用明确标记的原始细层差值包络。

### 重新评估条件

若全时域任一正式输出点的估计离散不确定度达到或超过 `5e-5`，才按时间/空间误差定位、局部聚类加密、减小 dt 的顺序整改；若全部满足，则停止加密并冻结最低成本可信配置。

### 状态

ACTIVE_TEAM_NUMERICAL_CRITERION

## D-Q2-001 Q2 主模型设计候选

日期：2026-09-11
问题：Q2

### 背景

Q2 将 Q1 的短时、常物性热/质扩散问题扩展为整个烘干过程，并由官方附录3给出同时依赖 `C` 与 `T` 的变物性公式。五份团队资料只能作为参考，不能替代官方 PDF。

### 设计决定

登记 `Q2-M1`：固定半径 `R=2 cm` 的一维圆柱径向模型，使用附录3的 `ρ(C)`、`cp(C)`、`k(C)`、`D(C,T)`，中心对称和表面热/质 Robin 边界作为候选，并通过耦合 Picard 交替更新 T/C。`C→ρ,cp,k`，`T,C→D` 的反馈必须显式进入时间步迭代。

### 理由与限制

该候选保持 Q1 可复用的几何和控制体结构，同时覆盖 Q2 官方新增的变物性与耦合要求。它不是已经验证的物理结论，也未授权修改 Q1 或生成 Q2 结果。

### 状态

DESIGN_CANDIDATE_NOT_IMPLEMENTED；重新评估条件为附录3单位/域测试、耦合 Picard、变量系数 benchmark 或人工物理审查失败。

## D-Q2-NUM-CANDIDATES Q2 数值候选矩阵

日期：2026-09-11
问题：Q2

保留 Candidate A（Q1 冻结聚簇 FVM + BE 首步/BDF2）和 Candidate B（uniform FVM + BE）用于实现后的同条件比较；Candidate C 仅在 A/B 的空间敏感性或边界层诊断需要时提出。当前不增加 Crank–Nicolson、全 Newton、FEM 等复杂方法。

### 状态

PENDING_IMPLEMENTATION_AUTHORIZATION；没有在本 Gate 选择胜者。

## D-Q2-COUPLING Q2 耦合 Picard 设计

日期：2026-09-11
问题：Q2

每个时间步以 `T^n,C^n` 作为初始猜测，按 block Gauss–Seidel 先解温度、再用最新温度解水分，并为两场分别计算归一化残差。`max_iter=50`、候选容差 `1e-8` 和可配置松弛因子均只继承为待验证候选。任何达到上限仍未收敛的步必须 fail-closed，并写出残差、松弛、物性范围、边界残差和失败位置。

### 状态

DESIGN_ONLY；尚未进入 `src/q2/` 实现。

## D-Q2-ENV-001 / D-Q2-ENV-002 环境处理

日期：2026-09-11
问题：Q2

官方附件1只覆盖到 `14400 s`。最后40点均值为 `T∞=49.99525°C`、`C∞=0.049988 kg/kg`，最后点为 `50.165°C`、`0.04986 kg/kg`；团队资料的 `50.00°C/0.0500` 是待确认常值建议。分段线性和 PCHIP 都保留，且不得修改或平滑官方数据点。

### 状态

OPEN；需人工决定尾段规则和插值主方案，再进入 Q2 实现。

## D-Q2-FVM-001 变系数界面平均

日期：2026-09-11
问题：Q2

算术平均是团队资料的方案，调和平均是梯度较强时的保守候选。设计上两者都要有可复现 benchmark、守恒/一致性/系数平滑性检查，不能在没有证据时把算术平均写成官方或最终数值决定。

### 状态

OPEN_NUMERICAL_DECISION。

## D-Q2-END-001 / D-Q2-ACC-001 Q2 终点与精度门

日期：2026-09-11
问题：Q2

题面规定表3/4展示到3 h，但“整个烘干过程”的计算终点未给出可直接冻结的行数。Q3 的 `C<0.15 kg/kg` 只能作为接口候选，不能自动成为 Q2 官方结束条件。Q1 的 `<5e-5` 团队数值门也不能直接继承为 Q2 结论；必须在长时累计误差、事件时刻敏感性、耦合迭代误差和运行成本复核后再决定。

### 状态

OPEN_INTERPRETATION / OPEN_TEAM_CRITERION。
