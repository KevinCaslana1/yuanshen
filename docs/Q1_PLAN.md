# Q1 Modeling Plan

> 状态：`MODEL DESIGN COMPLETE / WAITING IMPLEMENTATION APPROVAL`
>
> 本文件是 Q1 的问题分析与模型设计工作包，不是论文正文，不包含正式仿真结果、结果表或 `result1.xlsx`。本轮只完成题意核对、数据审计、候选模型、Baseline、假设、数值策略、验证计划和实验计划。

## Scope and Gate Boundary

- 本轮授权范围仅为 Q1。
- Q2、Q3、Q4 保持 `NOT STARTED`。
- 可以提出数学模型和算法设计，但不得进入正式求解、正式结果实验或最终交付文件生成。
- `A题/` 是 `OFFICIAL_SOURCE / IMMUTABLE_SOURCE`；本轮只读。
- 推荐模型表示“建议进入实现”，不表示已经证明最好。

## 1. Problem Restatement

Q1 研究预热平衡阶段药材内部温度与水分浓度的时空变化。药材近似为长 25 cm、半径 2 cm 的圆柱体，初始温度为 28 °C，初始干基含水率为 2.55 kg/kg。烘房温度和水分浓度由附件1给出，相关材料参数由附录2给出。

目标是建立能够描述圆柱形药材内部径向变化的模型，并为论文表1、表2提供指定时刻和指定径向位置的值；完整工程输出要求保存 1800 s 内、每隔 1 s、径向每隔 0.1 cm 的结果到 `result1.xlsx`。本阶段只定义如何计算和验证，不填充该文件。

## 2. Q1 Requirement Matrix

| Requirement | Content | Status | Evidence / Note |
|---|---|---|---|
| Input | 附件1中的烘房温度 `T∞(t)` 与水分浓度 `C∞(t)` | `STATEMENT_FACT` | `A题/附件/附件1.xlsx`；Q1使用 `0–1800 s` 区间 |
| Initial Condition | `T(r,0)=28 °C`，`C(r,0)=2.55 kg/kg` | `STATEMENT_FACT` | 官方题面问题1 |
| Geometry | 圆柱长 `L=25 cm`，半径 `R=2 cm` | `STATEMENT_FACT` | 官方题面问题1 |
| Parameter | `ρ=820 kg/m³`、`cp=2600 J/(kg·K)`、`k=0.36 W/(m·K)`、`h=25 W/(m²·K)`、`hm=8×10⁻⁷ m/s`、`D(C)=7×10⁻⁹ exp(-0.89/C) m²/s` | `STATEMENT_FACT` | 官方附录2 |
| Boundary Input | 将附件1的烘房温度和水分浓度作为外部边界输入 | `STATEMENT_FACT` | 官方题面与附录1 |
| Boundary Interpolation | 60 s 采样点之间采用不平滑的分段线性插值 | `MODELING_CHOICE` | 为获得 1 s 数值输入；不得删除或平滑原始点 |
| Target Variable | 药材内部 `T(r,t)` 与 `C(r,t)` | `STATEMENT_FACT` + `MODELING_CHOICE` | 官方要求时空规律；采用轴对称径向场表示 |
| Required Time Range | 论文表格：100、300、600、900、1200、1500、1800 s；完整结果：1800 s 内每隔 1 s | `STATEMENT_FACT` | 官方题面问题1；是否包含 `t=0` 保留 OQ-005 |
| Required Spatial Range | 到药材中心距离 `0, 0.5, 1, 1.5, 2 cm`；完整结果每隔 0.1 cm | `STATEMENT_FACT` | 官方题面问题1；端点计数保留 OQ-005/OQ-007 |
| Output Sampling | 时间 1 s；径向距离 0.1 cm | `STATEMENT_FACT` | 完整 `result1.xlsx` 要求 |
| Paper Table | 表1温度、表2水分浓度，行时间为指定 7 个时刻，列距离为 5 个位置 | `STATEMENT_FACT` | 官方题面第1页及 PDF 表1、表2 |
| Excel Output | `result1.xlsx`；Sheet 为 `温度`、`水分浓度`；A列时间，首行为到中心距离 | `STATEMENT_FACT` | 官方附录1/3；官方模板只读 |
| Precision | 所有最终结果保留四位小数 | `STATEMENT_FACT` | 官方题面 |
| Internal Temperature Unit | `T` 在内部统一用 K；输入和输出温度用 °C | `MODELING_CHOICE` | 绝对温度用于后续经验公式兼容性；Q1 的 `D` 只依赖 `C` |
| Full Output Shape | 由时间、空间采样规则展开，不能使用模板 5×6 作为最终尺寸 | `INTERPRETATION` | `docs/DELIVERABLE_SPEC.md`；OQ-001、OQ-005、OQ-007 |

## 3. Inputs and Q1 Data Audit

### 3.1 Official input inventory

| Input | Role | Read / Write | Audit status |
|---|---|---|---|
| `A题/A题.pdf` | 题面、附录2参数、结果格式 | Read-only | 已重新提取文本并视觉核对第1页、第3页 |
| `A题/附件/附件1.xlsx` | Q1外部边界输入 | Read-only | 已完成数据类型、时间、缺失、重复、范围审计 |
| `A题/附件/附件3/result1.xlsx` | Q1结果模板 | Read-only | 两个Sheet、5×6模板骨架通过校验 |

### 3.2 Attachment 1 structural audit

| Check | Result | Status |
|---|---|---|
| Worksheet | `Sheet1`，242行×3列，首行为表头，241条数据 | `PASS` |
| Time type | 整数秒 | `PASS` |
| Temperature type | 整数/浮点数值，无非数值数据 | `PASS` |
| Moisture type | 浮点数值，无非数值数据 | `PASS` |
| Time range | `0–14400 s` | `PASS` |
| Time interval | 所有相邻点为 `60 s` | `PASS` |
| Missing values | 未发现空值 | `PASS` |
| Duplicate times | 未发现重复时间 | `PASS` |
| Non-finite values | 未发现 NaN/Inf | `PASS` |
| Q1 window | `0–1800 s` 共 31 个原始边界点 | `PASS` |
| Raw data mutation | 未平滑、未删除、未覆盖、未外推 | `PASS` |

### 3.3 Boundary input range audit

| Quantity | Full attachment 1 range | Q1 range `0–1800 s` | Q1 first → last |
|---|---:|---:|---:|
| `T∞` | `28.000–50.246 °C` | `28.000–41.513 °C` | `28.000 → 41.513 °C` |
| `C∞` | `0.01963–0.05025 kg/kg` | `0.01963–0.03307 kg/kg` | `0.01963 → 0.03307 kg/kg` |

在 Q1 区间内，附件1中的温度和水分浓度均逐点上升；这是对官方数据的描述性审计，不是模型结论，也不用于拟合参数。Q1边界曲线的必要可视化对象已确定为 `T∞(t)` 和 `C∞(t)` 两条原始点/插值曲线，后续放入非正式数据审计或 `EXP-001` 产物中；本轮不把图表写入论文或结果文件。

### 3.4 Interpolation policy

附件1每 60 s 一个观测点，而 Q1 完整输出每 1 s 一个时间点。默认实现候选为分段线性插值：

\[
u_\infty(t)=u_j+\frac{t-t_j}{t_{j+1}-t_j}(u_{j+1}-u_j),
\quad t\in[t_j,t_{j+1}],
\]

其中 `u` 分别表示 `T∞` 或 `C∞`。这不是原始数据的平滑，也不改变官方数据点。零阶保持将作为输入处理敏感性实验的备选，不在设计阶段直接替换默认方案。Q1不需要对附件1做外推，因为目标时间区间完全位于 `0–14400 s` 内。

## 4. Required Outputs

### Paper-level outputs

- 表1：温度，时间 `100, 300, 600, 900, 1200, 1500, 1800 s`，距离 `0, 0.5, 1, 1.5, 2 cm`。
- 表2：水分浓度，时间和距离同上。
- 温度单位为 °C；水分浓度单位为 kg/kg；均保留四位小数。

### Engineering output

- 官方模板：`A题/附件/附件3/result1.xlsx`，只读。
- 候选输出：`deliverables/candidate/result1.xlsx`，只有在实现批准后才可由模板副本生成。
- Sheet：`温度`、`水分浓度`。
- A列时间单位为 s；首行空间坐标单位为 cm。
- 输出行列的端点和精确计数需遵循最终交付契约；当前由 OQ-001、OQ-005、OQ-007 约束。
- 本轮禁止创建或写入 `result1.xlsx`。

## 5. Known Parameters

| Symbol | Meaning | Value | Raw / Internal Unit | Source | Status |
|---|---|---:|---|---|---|
| `ρ` | 药材密度 | 820 | kg/m³ | 附录2 | `GIVEN` |
| `cp` | 比热容 | 2600 | J/(kg·K) | 附录2 | `GIVEN` |
| `k` | 热传导系数 | 0.36 | W/(m·K) | 附录2 | `GIVEN` |
| `h` | 对流换热系数 | 25 | W/(m²·K) | 附录2 | `GIVEN` |
| `hm` | 对流传质系数 | `8×10⁻⁷` | m/s | 附录2 | `GIVEN` |
| `D(C)` | 水分浓度扩散系数 | `7×10⁻⁹ exp(-0.89/C)` | m²/s | 附录2 | `GIVEN` |
| `L` | 圆柱长度 | 25 cm | 原始 cm；内部 m | 题面 | `GIVEN` |
| `R` | 初始半径 | 2 cm | 原始 cm；内部 0.02 m | 题面 | `GIVEN` |

## 6. Variables and Units

| Symbol | Meaning | Raw Unit | Internal Unit | Output Unit | Source | Status |
|---|---|---|---|---|---|---|
| `t` | 时间 | s | s | s / paper指定s | 题面、附件1 | `GIVEN` |
| `r` | 到药材中心的径向距离 | cm | m | cm | 题面、模板 | `GIVEN` |
| `R` | 药材表面初始半径 | cm | m | cm | 题面 | `GIVEN` |
| `L` | 药材长度 | cm | m | 不直接输出 | 题面 | `GIVEN` |
| `T_K(r,t)` | 药材温度 | °C输入/输出 | K | °C | 题面；模型内部约定 | `MODELING_CHOICE` |
| `T_C(r,t)` | 摄氏温度表示 | °C | 由 `T_K-273.15` 得到 | °C | 输出转换 | `DERIVED` |
| `T∞(t)` | 烘房温度 | °C | K | 不直接写入结果 | 附件1 | `GIVEN` + 插值为 `MODELING_CHOICE` |
| `C(r,t)` | 药材干基水分浓度 | kg/kg | kg/kg | kg/kg | 题面 | `GIVEN` / state variable |
| `C∞(t)` | 烘房水分浓度边界输入 | kg/kg | kg/kg | 不直接写入结果 | 附件1 | `GIVEN` + 插值为 `MODELING_CHOICE` |
| `D(C)` | 浓度扩散系数 | m²/s | m²/s | 不直接输出 | 附录2 | `DERIVED` |
| `q_T` | 热通量 | — | W/m² | 不直接输出 | PDE边界关系 | `DERIVED` |
| `j_C` | 浓度通量表述 | — | 与 `hm·C` 一致的模型单位 | 不直接输出 | PDE边界关系 | `DERIVED` |

所有几何计算在内部使用 m；温度的绝对值在内部使用 K；时间不从 s 隐式转换为 h；最终文件写入前才转换回题面要求的 °C、cm 和四位小数。

## 7. Geometry

### Main geometry candidate

采用圆柱坐标下的一维径向近似：

\[
0\le r\le R=0.02\ \mathrm{m},\qquad 0\le t\le1800\ \mathrm{s}.
\]

药材长度 `L=0.25 m` 用于说明长径比 `L/R=12.5`，主方案暂不解析轴向 `z` 变化。该选择必须作为高影响假设登记并在实现前审查；没有端面环境边界数据时，直接启用二维轴对称模型会引入额外未给定边界条件。

### Symmetry

温度和水分浓度均假定轴对称，不依赖角度和轴向坐标。中心 `r=0` 使用对称边界，表面 `r=R` 使用对流换热/传质边界。

## 8. Initial Conditions

\[
T_K(r,0)=28+273.15=301.15\ \mathrm{K},
\qquad
C(r,0)=2.55\ \mathrm{kg/kg},
\quad 0\le r\le R.
\]

初始场均匀是题面给出的初始信息的直接实现。实现时应在离散网格所有节点/控制体一致赋值，并检查初值没有 NaN、Inf 或超出物理表示范围。

## 9. Boundary Conditions

### Center symmetry

\[
\left.\frac{\partial T_K}{\partial r}\right|_{r=0}=0,
\qquad
\left.\frac{\partial C}{\partial r}\right|_{r=0}=0.
\]

### Surface heat transfer

主方案候选采用 Robin 边界：

\[
-k\left.\frac{\partial T_K}{\partial r}\right|_{r=R}
=h\,[T_K(R,t)-T_{\infty,K}(t)].
\]

当烘房温度高于表面温度时，等价形式 `k T_r = h(T∞-Ts)` 给出指向药材内部的正向加热效果。边界符号必须在 smoke test 中用升温方向检查。

### Surface mass transfer

主方案候选采用：

\[
-D(C_s)\left.\frac{\partial C}{\partial r}\right|_{r=R}
=h_m\,[C_s-C_\infty(t)],
\qquad C_s=C(R,t).
\]

这把附件1的烘房水分浓度解释为外部边界浓度，并使用附录2给出的对流传质系数。该干基浓度边界的物理解释和符号约定属于 OQ-006，必须在实现前人工审查。

## 10. Candidate Assumptions

正式候选假设全部登记在 `docs/ASSUMPTIONS.md`。当前状态均不是已接受结论：

1. `A-Q1-001`：Q1采用一维径向、轴向均匀和圆柱对称，属于 `HIGH IMPACT / NEEDS_REVIEW`。
2. `A-Q1-002`：Q1内半径固定，不考虑水分流失造成的收缩；尺寸变化留给Q4，属于 `HIGH IMPACT / PROPOSED`。
3. `A-Q1-003`：`ρ、cp、k、h、hm` 使用附录2常数，`D` 按 `C` 变化，属于 `HIGH IMPACT / PROPOSED`。
4. `A-Q1-004`：边界输入在 60 s 采样点之间采用分段线性插值，不做平滑或拟合，属于 `MEDIUM IMPACT / PROPOSED`。
5. `A-Q1-005`：表面采用 Robin 换热/传质边界，不直接令内部表面等于烘房输入，属于 `HIGH IMPACT / NEEDS_REVIEW`。
6. `A-Q1-006`：Q1忽略潜热、热质交叉耦合和内部源项，因为题面未给出所需系数；属于 `HIGH IMPACT / NEEDS_REVIEW`。
7. `A-Q1-007`：中心对称边界与表面单向通量边界足以描述 Q1 目标时段，属于 `MEDIUM IMPACT / PROPOSED`。

## 11. Candidate Models

### Baseline Candidate B0: lumped exchange model

将药材视为温度和水分浓度在空间上均匀的控制体，使用与主方案相同的外部输入和传递系数：

\[
\frac{dT_K}{dt}=\frac{hA}{\rho c_pV}(T_{\infty,K}-T_K),
\qquad
\frac{dC}{dt}=h_m\frac{A}{V}(C_\infty-C).
\]

主设计中取长圆柱侧面积与体积的比值 `A/V=2/R`，以保持与一维径向、忽略端面效应的几何约定一致。B0 的作用是提供低成本时间尺度和方向性 sanity check，不满足 Q1 的空间输出要求，因此不是最终候选。

### Main Candidate M1: nonlinear radial diffusion with Robin boundaries

温度场：

\[
\rho c_p\frac{\partial T_K}{\partial t}
=\frac1r\frac{\partial}{\partial r}\left(kr\frac{\partial T_K}{\partial r}\right).
\]

水分场：

\[
\frac{\partial C}{\partial t}
=\frac1r\frac{\partial}{\partial r}\left(D(C)r\frac{\partial C}{\partial r}\right),
\qquad
D(C)=7\times10^{-9}\exp\left(-\frac{0.89}{C}\right).
\]

配合第8节初值、第9节中心对称和表面 Robin 边界，M1 能输出 `0≤r≤R` 的温度与浓度场，保留 `D(C)` 的非线性，并与题面给出的 Q1 参数一致。M1 的主要风险是干基浓度 Robin 边界的物理解释、中心离散以及非线性求解稳定性。

### Alternative Candidate M2: constant-D radial diffusion

用一个登记过的代表浓度 `C_ref` 计算常数 `D(C_ref)`，其余设置同 M1。M2 数值上更简单，可作为消融和稳定性对照，但会丢失 `D` 随 `C` 变化的特征，不能未经比较就替代 M1。

### Alternative Candidate M3: Dirichlet surface approximation

直接使用 `T_K(R,t)=T∞,K(t)`、`C(R,t)=C∞(t)` 的表面值边界。M3 可作为边界敏感性对照，计算简单，但忽略题面给出的 `h` 和 `hm` 所代表的表面传递阻力，物理匹配度低于 Robin 主方案。

### Alternative Candidate M4: two-dimensional axisymmetric model

解析 `r-z` 方向并加入端面边界。M4 理论上能表示端部效应，但题面没有端面换热/传质边界数据，参数和计算成本显著增加；在 Q1 中仅作为风险审查对象，不建议在没有人工授权和新数据前实现。

## 12. Baseline Design Review

| Criterion | B0 lumped | M1 radial nonlinear | M2 constant-D | M3 Dirichlet | M4 2D |
|---|---|---|---|---|---|
| Spatial output | 不支持，只给均匀值 | 支持 | 支持 | 支持 | 支持 |
| Physics match | 低到中 | 高 | 中 | 中低 | 数据不足 |
| Nonlinearity | 无 | 保留 `D(C)` | 删除 | 保留/删除视实现 | 可保留 |
| Numerical cost | 极低 | 中 | 低 | 低到中 | 高 |
| Interpretability | 很高 | 高 | 高 | 高 | 中 |
| Main risk | 无空间梯度 | 边界和非线性求解 | 代表 `D` 选择 | 传递阻力被忽略 | 端面边界缺失 |
| Role | 必须 Baseline | 推荐实现候选 | 消融/对照 | 边界敏感性 | 暂不实现 |

B0 保留的理由是它简单、可复现且不是故意错误的模型；它可以回答“空间扩散模型是否带来必要的信息”，同时为 M1 的平均响应提供 sanity check。

## 13. Main Model Candidate and Recommendation

### Recommended Candidate

建议进入实现的候选为 **M1：一维径向、轴对称、非线性水分扩散 + 常物性热传导 + Robin 表面换热/传质边界**。推荐理由是：

- 能直接覆盖 Q1 的空间输出要求；
- 使用附录2给出的全部 Q1 参数，并保留 `D(C)` 的已给经验关系；
- Robin 边界显式使用 `h` 和 `hm`，比直接 Dirichlet 更贴合题面参数结构；
- 计算成本和验证复杂度仍可控；
- 可以与 B0、M2、M3 形成清晰对照。

该推荐不是“已经证明最好”。`A-Q1-001`、`A-Q1-005`、`A-Q1-006` 需要在实现前进行人工复核，标记为 `REQUIRES HUMAN REVIEW`。

## 14. Numerical Strategy Candidates

### N1: conservative radial finite volume + implicit stepping (recommended)

- 在 `r∈[0,R]` 上使用包含 `r=0` 和 `r=R` 的径向网格，输出网格候选步长 `Δr=0.001 m`，与 0.1 cm 直接对齐。
- 以面通量离散径向扩散项，中心面通量设为 0；表面面通量由 Robin 关系计算。
- 温度和水分分别组装离散方程；水分扩散系数在每一时间步由当前 `C` 更新。
- 优先使用 backward Euler 作为稳健起点；内部步长可小于输出间隔，输出时再采样到每 1 s。
- 非线性水分方程采用 Picard 迭代或阻尼 Newton；每个时间步记录残差和最大迭代次数。

### N2: method of lines + BDF

将空间离散后交给 BDF 类刚性 ODE 求解器。优点是时间自适应，缺点是外部求解器、边界事件和可复现步长控制更复杂，作为后续替代实现。

### N3: explicit finite difference

适合最小 smoke test，但受扩散稳定性条件限制，正式 1 s 输出间隔不能直接等同于稳定时间步。只用于验证离散方向和小网格，不作为默认正式求解策略。

### Numerical implementation contract

实现批准后，必须记录：网格节点定义、中心离散公式、表面 Robin 离散公式、内部步长、非线性容差、最大迭代数、收敛失败处理、输出采样和单位转换。任何插值、平滑、外推或边界替代都必须先登记为 `MODELING_CHOICE`。

## 15. Validation Plan

| Check | Applicable? | Planned method | Acceptance criterion |
|---|---|---|---|
| Initial conditions | Yes | 首个状态与题面初值逐点比较 | 所有内部节点满足 `T=28 °C`、`C=2.55 kg/kg`，容差预先配置 |
| Unit consistency | Yes | 静态单位表 + 运行时范围检查 | m/K/s 与输出 cm/°C/s 的转换显式，无隐式 h↔s |
| NaN/Inf | Yes | 每个输出状态检查 | 无 NaN/Inf |
| Numerical range | Yes | 温度、浓度和系数范围检查 | 不出现未解释的负浓度或极端发散值 |
| Center symmetry | Yes | 检查中心通量和中心梯度 | 中心边界通量为零，离散残差在容差内 |
| Surface boundary behavior | Yes | Robin 通量独立复算 | 离散表面通量与边界关系一致，升温/失水方向正确 |
| Time continuity | Yes | 1 s 输出序列和内部步长日志 | 无跳步、重复时间或非递增时间 |
| Spatial continuity | Yes | 相邻节点差分与剖面检查 | 无非物理棋盘格或孤立尖峰；具体阈值在实现前登记 |
| Time-step sensitivity | Yes | EXP-003 | 结果差异达到预设容差并记录 |
| Spatial convergence | Yes | EXP-004 | 关键表格点随网格细化趋于稳定 |
| Mass/energy sanity | Conditional | 计算边界通量与内部储量变化 | 若采用当前方程，离散守恒残差可解释；潜热未纳入时不宣称完整能量守恒 |
| Baseline comparison | Yes | EXP-002 | B0 与 M1 的平均响应方向一致，差异可解释 |
| Data leakage / CV | No for Q1 PDE | 不做机器学习划分 | 记录为不适用，不机械执行 |
| Residual analysis | Conditional | 仅在参数校准或外部观测拟合时启用 | 当前无拟合，不虚构残差结论 |

## 16. Experiment Plan

以下实验均为 `PLANNED`，本轮未运行，不能作为论文证据。

| ID | Purpose / Question | Model | Config / Input | Expected Evidence | Acceptance Criteria | Estimated Runtime |
|---|---|---|---|---|---|---|
| EXP-001 | 检查输入读取、插值、单位转换、边界方向和最小离散是否可运行 | M1 smoke | 极小径向网格、短时间窗口、附件1原始点 | 日志、边界输入曲线、无写入官方模板 | 可重复运行；无 NaN/Inf；初值和边界方向检查通过 | <1 min |
| EXP-002 | 判断空间扩散是否相对均匀 Baseline 必要 | B0 vs M1 | 同一 Q1 输入、短时和完整设计时长两档 | 均匀平均响应与径向响应对照 | 差异有明确解释；不以单一指标决定模型 | <2 min |
| EXP-003 | 检查时间离散敏感性和刚性处理 | M1 | 内部 `Δt` 候选：输出步长及更小步长 | 关键位置/时刻差异表 | 差异低于预设容差，或记录不稳定原因 | <5 min |
| EXP-004 | 检查空间网格收敛 | M1 | `Δr=0.1, 0.05, 0.025 cm` 候选 | 网格细化误差和剖面 | 关键输出量趋于稳定，中心/表面不出现伪振荡 | <10 min |
| EXP-005 | 检查 Robin 与 Dirichlet 边界处理影响 | M1 vs M3 | 相同输入和网格 | 表面滞后、中心响应和边界通量对照 | 说明边界假设对结果的影响；不预设谁“更好” | <5 min |
| EXP-006 | 检查分段线性与零阶保持输入处理差异 | M1 | 同一原始附件1，不改原始点 | 输入处理敏感性表 | 若差异显著，升级为人工审查事项 | <5 min |
| EXP-007 | 检查通量、储量和物理范围 | M1 | 完整 Q1 设计时长、收敛配置 | 质量/能量相关 sanity 日志 | 守恒残差可解释，所有范围异常有记录 | <5 min |

## 17. Risks

1. **高影响几何风险**：一维径向假设忽略端部效应；题面没有端面边界输入，需人工确认适用范围。
2. **高影响边界风险**：`hm` 对干基水分浓度的 Robin 解释可能影响表面浓度和内部梯度。
3. **高影响物理简化风险**：当前 Q1 设计未纳入潜热和热质交叉耦合，不能在验证前宣称完整热质耦合模型。
4. **数值风险**：中心 `1/r` 项和表面 Robin 离散容易出现符号或几何因子错误，必须用通量复算与 smoke test 检查。
5. **数据处理风险**：1 s 输出要求来自 60 s 输入，插值选择会影响早期边界变化；不得无记录平滑或外推。
6. **交付风险**：官方模板是 5×6 骨架，不是最终尺寸；实现时必须写入 candidate 副本并通过交付契约校验。

## 18. Open Questions

| ID | Type | Q1 issue | Blocking Phase | Current handling |
|---|---|---|---|---|
| OQ-001 | `DELIVERABLE` | 完整结果的时间/空间端点计数与模板展开规则 | Deliverable Generation | 保持 `OPEN_QUESTION`，不在本轮硬编码 |
| OQ-005 | `DELIVERABLE` | `result1.xlsx` 是否包含 `t=0` 行；模板示例从 1 开始但不应替代题面 | Deliverable Generation | 实现前人工确认 |
| OQ-006 | `MODELING` | `hm` 与干基 `C` 的 Robin 边界物理解释及符号约定 | Model Implementation | 作为 `REQUIRES HUMAN REVIEW`，先做通量 smoke test |
| OQ-007 | `NUMERICAL` | `r=0` 与 `r=R` 输出值采用节点值、边界值还是插值值 | Numerical Implementation | 在网格定义和交付契约中明确 |
| OQ-008 | `MODELING` | 是否需要加入潜热、热质交叉耦合或内部源项 | Model Implementation | 当前标为高影响假设，缺少题面参数，不自行扩展 |
| OQ-002 | `INTERPRETATION` | Q2 的时间背景与 Q1 无关 | Q2 Model Implementation | 保持未决，不在 Q1 处理 |
| OQ-003 | `DELIVERABLE` | Q3/Q4 结束时间行与 Q1 无关 | Q3/Q4 Deliverable Generation | 保持未决，不在 Q1 处理 |
| OQ-004 | `MODELING` | Q4 动态半径与空间网格同步与 Q1 无关 | Q4 Model Implementation | 保持未决，不在 Q1 处理 |

## 19. Definition of Done

Q1 Model Design Gate 只有在以下事项全部完成后才算完成：

- [x] 重新阅读官方题面、附录2、附件1说明和 `result1.xlsx` 模板结构。
- [x] 建立 Q1 Requirement Matrix，区分 `STATEMENT_FACT`、`INTERPRETATION`、`MODELING_CHOICE`。
- [x] 完成附件1的数据类型、时间范围、间隔、缺失、重复、异常格式、单位和范围审计。
- [x] 建立变量与单位表，明确 °C/K、cm/m、s 的转换。
- [x] 登记候选数学假设及高影响风险。
- [x] 建立 Baseline、Main Candidate 和 Alternative Candidates，并比较适用性。
- [x] 设计数值离散、边界实现、插值、稳定性和收敛检查。
- [x] 建立 Q1 Validation Plan 和 `EXP-001`–`EXP-007` 计划。
- [x] 完成 Model Design Review，并将推荐候选标记为“建议进入实现”。
- [x] 没有生成正式结果、正式实验、论文结论或 `result1.xlsx`。

## 20. Model Design Review

| Role | Candidate | Review status |
|---|---|---|
| Baseline | B0 lumped exchange model | Registered; required for later comparison |
| Main Candidate | M1 nonlinear radial diffusion with Robin boundaries | Recommended for implementation, not yet approved |
| Alternative 1 | M2 constant-D radial diffusion | Registered for ablation/stability comparison |
| Alternative 2 | M3 Dirichlet surface approximation | Registered for boundary sensitivity only |
| Alternative 3 | M4 2D axisymmetric model | Not recommended before new boundary information and human review |
| Recommended Candidate | M1 | `REQUIRES HUMAN REVIEW` for A-Q1-001/A-Q1-005/A-Q1-006 and OQ-006/OQ-008 |

**Gate result**：Q1 设计材料已完成，但正式实现仍需人工授权。本文件不授权自动启动数值求解。
