# Q1 Numerical Convergence Diagnosis & Remediation Audit

日期：2026-09-11  
范围：仅 Q1；Q2–Q4 未启动。  
代码/证据基线：`843d62861b7137f93222f01df61609a228ceab5a`  
官方输入：`A题/附件/附件1.xlsx`，SHA-256=`7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7`。  
交付约束：本轮不生成 `result1.xlsx`，不写入 `A题/`、`deliverables/candidate/` 或 `deliverables/final/`。

## Current Project Status

Q1 当前仍处于 `NUMERICAL REMEDIATION BLOCKED`。M1 生产实现的径向有限体积装配、中心/表面半控制体积、Robin 行、BE 时间层级、Picard 迭代和输出对齐已完成代码审计；独立制造解 benchmark 支持空间二阶、BE 时间一阶。真实 Q1 的 BE 误差诊断显示温度时间误差和含水率早期/表面误差仍是主要风险。

已测试的 M1-NUM-T2 是“一阶 BE 启动一步，然后 BDF2”的数值候选。它改善了论文 7×5 点的四位小数稳定性，但全网格含水率的保守 Richardson 剩余误差仍超过四位小数半单位，因此不能冻结为最终方法，也不能生成 `result1.xlsx`。

- 当前问题：Q1 数值收敛与结果交付精度。
- 已完成：启动协议、Q1 实现与内部验证、最终精度阻塞记录、数值实现审计、独立 benchmark、误差定位、Picard 敏感性、BDF2 候选对照。
- 主方案：M1，一维径向非线性扩散 + Robin 边界 + Backward Euler；尚未成为最终冻结模型。
- Baseline：B0；M2/M3 作为对照。
- 已知失败：`EXP-Q1-FINAL-CONV` 阻塞；BDF2 候选只通过论文点稳定性，未通过全网格安全裕量。
- 阻塞项：完整交付网格的估计误差/四舍五入安全性；需人工决定是否继续做局部早期/表面诊断。
- 最高优先级：人工审查本报告，不放宽门槛、不生成工作簿、不启动 Q2。

## Numerical Implementation Audit

### Geometry and coefficient mapping

生产代码位于 `src/q1/model.py`，时间推进位于 `src/q1/solver.py`。方程按圆柱轴向长度和公共 `2πL` 因子约去后的径向控制体积实现。内部计算单位显式为 `m`、`s`、`K`、`kg/kg`；参数单位包括 `ρ: kg/m^3`、`cp: J/(kg·K)`、`k: W/(m·K)`、`h: W/(m²·K)`、`hm: m/s`、`D: m²/s`。输出温度转换为 `°C`，位置输出为 `cm`；未在内部计算中提前四舍五入。

对单个物理场 `u`，储存系数记为 `capacity`，热场取 `ρcp`，水分场取 `1`。给定节点值 `u_i^n`、时间步 `Δt`、面扩散系数 `D_{i+1/2}` 和网格间距 `Δr`，生产装配的三对角行映射如下：

- 中心 `i=0`：控制体积因子为 `Δr²/8`，零通量对称条件给出 `lower[0]=0`，`a0=4ΔtD_{1/2}/(capacity·Δr²)`，`main[0]=1+a0`，`upper[0]=-a0`，`RHS[0]=u_0^n`。
- 内部节点 `1≤i≤N-1`：控制体积因子为 `iΔr²`；`r_{i-1/2}=(i-1/2)Δr`、`r_{i+1/2}=(i+1/2)Δr`。`left=Δt·r_{i-1/2}D_{i-1/2}/(capacity·iΔr³)`，`right=Δt·r_{i+1/2}D_{i+1/2}/(capacity·iΔr³)`；`lower[i]=-left`，`main[i]=1+left+right`，`upper[i]=-right`，`RHS[i]=u_i^n`。
- 表面 `i=N`：内侧半控制体积因子为 `V_s=0.5[R²-(R-Δr/2)²]`，储存项为 `capacity·V_s`。Robin 内侧系数为 `inner=Δt·(R-Δr/2)D_{N-1/2}/(capacity·V_s·Δr)`，外侧系数为 `external=Δt·R·transfer/(capacity·V_s)`；`lower[N]=-inner`，`main[N]=1+inner+external`，`upper[N]=0`，`RHS[N]=u_N^n+external·u_∞^{n+1}`。其中 `transfer` 对温度为 `h`，对水分为 `hm`。
- 表面 Robin 符号：`boundary_flux_outward = transfer·(u_s-u_∞)`；当表面值高于环境值时外向通量为正，代入离散行后环境项以正号进入 RHS。
- 表面 Dirichlet 对照：末行为 `lower=0, main=1, upper=0, RHS=u_∞`，仅用于 M3 敏感性，不是当前主边界。
- 水分 `D(C)`：节点扩散系数由当前 Picard 猜测得到，面值使用相邻节点算术平均；温度使用附录参数给出的常导热系数。

### Time levels, Picard, and output alignment

BE 的每一步使用 `u^n` 作为储存项旧值，并在 `t_{n+1}` 读取边界输入，求出并保存 `u^{n+1}`。水分 Picard 以旧时间层作 RHS，以当前猜测计算 `D(C)`，使用归一化最大节点差判定收敛，并保存最后一次收敛场。`N=80/160/320` 的网格间距分别为 `0.25/0.125/0.0625 mm`，均严格包含 `0.0,0.1,...,2.0 cm` 输出位置；`dt=1/0.5/0.25 s` 均严格包含 `1..1800 s` 物理时刻。

### Audit verdict

未发现 lower/main/upper/RHS、中心几何、表面半体积、Robin 面积/符号/单位、面扩散系数、BE 层级、Picard 或输出时间/位置错位缺陷。独立 benchmark 的二阶空间和一阶 BE 时间结果支持该结论。真实 Q1 的高误差应先解释为离散误差分布/模型边界选择风险，而不是未经证据认定为生产实现 bug。

## Error Localization

比较均使用相同物理时刻和相同输出位置：完整网格为 `t=1..1800 s × r=0.0..2.0 cm`，共 `37,800` 个单元/场；论文网格为 `7×5=35` 个点。误差定位图保存在 `experiments/EXP-Q1-NUM-DIAG/`。

| Comparison | Field | L∞ 最大位置与数值 | `t≤300 s` 峰值/全局峰值 | `r≥1.8 cm` 平均误差占比 |
|---|---|---:|---:|---:|
| N160→N320 | 温度 | `t=300 s,r=2.0 cm`; `2.299618e-5 °C` | `1.0000` | `0.3609` |
| N160→N320 | 含水率 | `t=1 s,r=2.0 cm`; `0.005651325 kg/kg` | `1.0000` | `0.7660` |
| dt0.5→dt0.25 | 温度 | `t=897 s,r=0`; `4.776183e-4 °C` | `0.5518` | `0.1073` |
| dt0.5→dt0.25 | 含水率 | `t=1 s,r=2.0 cm`; `0.001165739 kg/kg` | `1.0000` | `0.6366` |

结论：温度空间误差在表面更显著但量级小；BE 温度时间误差是完整网格主要温度风险；含水率的最大误差明确集中在早期时间和表面，不能用最终时刻或论文点单独代表全网格。

## Spatial Convergence

固定 `dt=0.25 s`，比较 `N=80/160/320`，下表报告 N160→N320 的 Level 1 原始差异；`p=log(E_160→320? )` 按相邻细化差异比计算，Richardson 剩余估计为 `E_fine/(2^p-1)`。表中 `p` 和剩余估计使用 L∞ 序列，mean/RMSE 同时保留用于审计。

| Field / region | L∞ | mean abs | RMSE | p | Richardson remaining L∞ |
|---|---:|---:|---:|---:|---:|
| 温度 / full grid | `2.299618e-5` | `3.618688e-6` | `5.073491e-6` | `1.999865` | `7.666347e-6` |
| 温度 / center | `5.557043e-6` | `2.299382e-6` | `2.928299e-6` | `1.999156` | `1.853793e-6` |
| 温度 / surface | `2.299618e-5` | `1.038070e-5` | `1.176290e-5` | `1.999865` | `7.666347e-6` |
| 温度 / paper points | `2.299618e-5` | `4.134507e-6` | `6.474773e-6` | `1.999865` | `7.666347e-6` |
| 含水率 / full grid | `5.651325e-3` | `1.504981e-5` | `6.615242e-5` | `1.094222` | `4.979235e-3` |
| 含水率 / center | `9.781105e-8` | `8.958983e-9` | `2.194954e-8` | `2.016339` | `3.211596e-8` |
| 含水率 / surface | `5.651325e-3` | `1.170339e-4` | `2.837142e-4` | `1.094222` | `4.979235e-3` |
| 含水率 / paper points | `3.504741e-4` | `2.287432e-5` | `6.768097e-5` | `2.022690` | `1.144066e-4` |

空间温度、中心含水率和论文点含水率接近二阶；全网格/表面含水率 L∞ 被 `t=1 s,r=2 cm` 的早期边界层误差主导，不能把局部二阶结果外推为全网格二阶。

## Temporal Convergence

固定 `N=320`，比较 `dt=1/0.5/0.25 s`。下表报告 BE 的 dt0.5→dt0.25 Level 1 原始差异及估计。BE 理论上不应期待时间阶超过 1。

| Field / region | L∞ | mean abs | RMSE | p | Richardson remaining L∞ |
|---|---:|---:|---:|---:|---:|
| 温度 / full grid | `4.776183e-4` | `3.0099996e-4` | `3.225244e-4` | `0.999262` | `4.781073e-4` |
| 温度 / center | `4.776183e-4` | `3.444069e-4` | `3.740848e-4` | `0.999262` | `4.781073e-4` |
| 温度 / surface | `2.961580e-4` | `2.121686e-4` | `2.167378e-4` | `0.998993` | `2.965721e-4` |
| 温度 / paper points | `4.776070e-4` | `2.790932e-4` | `3.046057e-4` | `0.999257` | `4.780995e-4` |
| 含水率 / full grid | `1.165739e-3` | `6.979366e-6` | `1.788754e-5` | `0.773797` | `1.642433e-3` |
| 含水率 / center | `6.514810e-8` | `5.948747e-9` | `1.459418e-8` | `1.009823` | `6.426994e-8` |
| 含水率 / surface | `1.165739e-3` | `4.624145e-5` | `6.994493e-5` | `0.773797` | `1.642433e-3` |
| 含水率 / paper points | `1.022922e-4` | `1.059616e-5` | `2.330408e-5` | `0.999312` | `1.023899e-4` |

BE 温度时间 L∞ 与理论一阶一致；含水率中心/论文点接近一阶，但全网格/表面 L∞ 受早期表面误差和局部非光滑响应影响，不能以全网格 L∞ 宣称理想一阶常数。

## Picard Sensitivity

短验证配置为 `300 s、N=160、dt=0.25 s`。

| Picard tolerance | max iterations | mean iterations |
|---:|---:|---:|
| `1e-6` | `2` | `2.0000` |
| `1e-8` | `3` | `3.0000` |
| `1e-10` | `4` | `3.0842` |

`1e-6→1e-8` 的温度 L∞ 差为 `0`，含水率 L∞ 差为 `1.585329e-9 kg/kg`；`1e-8→1e-10` 的含水率 L∞ 差为 `1.700862e-13 kg/kg`。相比真实 Q1 的空间/时间 L∞ 差，Picard 误差可忽略，当前整改不需要继续收紧 Picard 容差。

## Numerical Benchmark Result

独立 benchmark `EXP-Q1-NUM-BENCH` 不读取生产输入，使用 `u(r,t)=e^{-t}(1+r^4)`、常数 `D=0.1`、源项 `e^{-t}(-1-r^4-16Dr²)` 和 Robin 环境值 `u(R,t)+D u_r(R,t)/h`。空间测试使用 `N=40/80/160/320`，并按网格缩小步长以压低时间误差；BE 时间测试固定 `N=320`，使用 `dt=0.002/0.001/0.0005/0.00025`。

- BE 空间 L∞ 观测阶：`1.9715, 1.9938, 1.9985`；中心和表面保持相同收敛趋势。
- BE 时间 L∞ 观测阶：`1.0096, 1.0146, 1.0089`；mean/RMSE 也约为一阶。
- BDF2 时间首个细化的 L∞ 观测阶为 `1.9906`，之后受空间误差底影响，L∞ 阶不再单调；因此只把首个二阶证据作为候选支持，不把后续非单调序列包装成最终理论验证。
- benchmark 运行时间约 `4.43 s`，生产输入使用标记为 `false`，生产模型未因 benchmark 改写。

该结果支持“当前生产装配基本阶数正确”的判断，同时区分了离散误差与物理模型误差：benchmark 只验证数值离散，不验证 Robin 干基浓度解释、忽略潜热/交叉耦合或一维假设的物理正确性。

## Boundary Verification

新增 `tests/test_q1_robin_boundary.py`，验证：中心和表面半控制体积因子、独立推导的 Robin 表面 lower/main/upper/RHS、Robin 外向通量正号、Dirichlet 末行，以及 BDF2 Robin 行的 `2/3` 算子缩放和两层历史项。运行结果为 `29 passed`。

旧有 `EXP-005` 仍显示 Robin 与 Dirichlet 是高影响建模选择；测试通过只证明当前代码实现与所登记的 Robin 口径一致，不证明官方唯一物理解释已被验证。

## Remediation Performed

1. 审计 `src/q1/model.py`、`src/q1/solver.py` 的几何、系数、边界、单位、时间层级、Picard 和输出对齐。
2. 新增隔离制造解 benchmark、Level 1–3 真实 Q1 诊断、时间/半径误差定位 SVG 和 Picard 容差敏感性。
3. 新增 `assemble_bdf2_radial_system`、`implicit_bdf2_radial_step` 和 `run_m1_bdf2`；BDF2 采用一阶 BE 启动一步，之后保持相同物理模型、Robin 边界和 Picard 过程。
4. 修正 benchmark 初版中 Robin 环境导数漏乘 `e^{-t}` 的 harness 错误；修正后的结果才进入正式 `EXP-Q1-NUM-BENCH` 证据。
5. 没有修改官方题目、附件或结果模板；没有生成 candidate/final 工作簿。

## Backward Euler vs BDF2

BDF2 候选实验为 `N=320`、`dt=1/0.5/0.25 s`，并以 BE `dt=0.25 s` 作参考。

| Comparison | Field | Full-grid L∞ | Full-grid rounded diff | Paper-point L∞ | Paper rounded diff |
|---|---|---:|---:|---:|---:|
| BDF2 dt1→dt0.5 | 温度 | `4.239982e-5 °C` | `583/37800` | `5.556053e-6 °C` | `1/35` |
| BDF2 dt1→dt0.5 | 含水率 | `3.132780e-3 kg/kg` | `30/37800` | `1.509391e-6 kg/kg` | `0/35` |
| BDF2 dt0.5→dt0.25 | 温度 | `1.521459e-5 °C` | `136/37800` | `1.386569e-6 °C` | `0/35` |
| BDF2 dt0.5→dt0.25 | 含水率 | `1.115133e-3 kg/kg` | `12/37800` | `3.786113e-7 kg/kg` | `0/35` |

针对 BDF2 dt0.5→dt0.25 的 L∞ 观测阶/剩余估计：温度 full grid `p=1.478603`、剩余 `8.515052e-6 °C`；温度论文点 `p=2.002541`、剩余 `4.611061e-7 °C`；含水率 full grid `p=1.490228`、剩余 `6.163227e-4 kg/kg`；含水率论文点 `p=1.995177`、剩余 `1.267679e-7 kg/kg`。

BE 与 BDF2 在同一 `dt=0.25 s` 下的场差为：温度 full-grid L∞ `4.776655e-4 °C`、论文点 `4.776565e-4 °C`；含水率 full-grid L∞ `1.089036e-3 kg/kg`、论文点 `1.021982e-4 kg/kg`。这证明时间积分改变确实影响结果，但不构成 BDF2 已满足全网格交付精度的证明。

## Recommended Numerical Configuration

当前不推荐任何配置进入最终交付。若人工批准继续做下一轮数值工作，优先把 `M1-NUM-T2, N=320, dt=0.25 s` 作为诊断候选，因为它在 benchmark 和论文点上有明确改善；这不是最终冻结决定。

下一轮应先针对 `t≤300 s`、`r≥1.8 cm` 的含水率误差做最小局部诊断，复核 Robin 表面处理、启动步和早期边界输入对结果的影响；不能直接跳到 `dt=0.125 s` 或无限追求 `37800` 个单元的 rounded count。只有在完整网格 Level 1–3、benchmark、Picard、守恒/范围和安全裕量共同通过后，才可返回 Q1 Result & Deliverable Gate。

## Four-decimal Stability

四舍五入采用 `ROUND_HALF_UP`，半单位为 `0.5e-4`；rounded disagreement 仅作辅助门，不能替代 raw/Richardson 误差。BDF2 dt0.5→dt0.25 的论文点为温度 `0/35`、含水率 `0/35`，但全网格仍为温度 `136/37800`、含水率 `12/37800`。

逐单元阈值距离定义为当前细网格值到最近的 `(k+0.5)e-4` 的绝对距离，并与保守 L∞ Richardson 剩余估计比较：

| Field / region | Estimated remaining L∞ | Min threshold distance | Unsafe cells (`estimate ≥ distance`) |
|---|---:|---:|---:|
| 温度 / full grid | `8.515052e-6 °C` | `4.957430e-10 °C` | `6233/37800` |
| 温度 / center | `3.079863e-7 °C` | `6.034074e-9 °C` | `9/1800` |
| 温度 / surface | `8.515052e-6 °C` | `8.560717e-8 °C` | `314/1800` |
| 温度 / paper points | `4.611061e-7 °C` | `1.285143e-6 °C` | `0/35` |
| 含水率 / full grid | `6.163227e-4 kg/kg` | `3.920813e-9 kg/kg` | `37800/37800` |
| 含水率 / center | `6.214500e-11 kg/kg` | `4.237171e-5 kg/kg` | `0/1800` |
| 含水率 / surface | `6.163227e-4 kg/kg` | `8.486577e-8 kg/kg` | `1800/1800` |
| 含水率 / paper points | `1.267679e-7 kg/kg` | `7.821681e-6 kg/kg` | `0/35` |

因此“论文点稳定”与“全网格安全”必须分开报告；当前全网格安全性未通过。

## Validation Summary

- 生产实现审计：PASS（未发现离散/边界/时间层级实现缺陷）。
- 独立制造解 benchmark：PASS，BE 空间约二阶、时间约一阶；BDF2 首个细化显示二阶候选行为。
- Robin/中心边界单元测试：PASS，`29 passed`。
- Picard 敏感性：PASS，迭代误差远小于离散误差。
- 误差定位：PASS，已定位早期时间和表面带。
- BDF2 数值整改：PARTIAL，论文点改善，完整网格未通过。
- Q1 Result & Deliverable Gate：BLOCKED。
- `result1.xlsx`：未生成。
- Q2–Q4：`NOT STARTED`。

## Remaining Risks

- Robin 传质边界中 `hm` 直接作用于干基浓度是已登记的团队建模解释，不是官方唯一事实。
- 一维径向、固定半径、忽略潜热/热质交叉耦合仍是高影响建模假设；本轮只处理数值收敛，不重新冻结物理模型。
- BDF2 的启动步和早期表面含水率误差尚未通过针对性复验；不可把论文点结果外推到全网格。
- 现有守恒/能量 sanity check（EXP-007）支持 BE 当前方程的内部一致性，但未授权把其直接扩展为 BDF2 最终验证结论。
- 没有实测校准或外部实验数据；数值收敛不等于物理真实性。

## Files Created

- `scripts/run_q1_num_benchmark.py`
- `scripts/run_q1_num_diag.py`
- `scripts/run_q1_num_remediation.py`
- `scripts/run_q1_picard_sensitivity.py`
- `tests/test_q1_robin_boundary.py`
- `experiments/EXP-Q1-NUM-BENCH/`
- `experiments/EXP-Q1-NUM-DIAG/`
- `experiments/EXP-Q1-PICARD-SENS/`
- `experiments/EXP-Q1-NUM-REMEDIATION/`
- 本文件

## Files Modified

- `src/q1/model.py`
- `src/q1/solver.py`
- `docs/EXPERIMENTS.md`
- `docs/FAILURES.md`
- `docs/FINDINGS.md`
- `docs/DECISIONS.md`
- `docs/HYPOTHESES.md`
- `docs/VALIDATION.md`
- `docs/TODO.md`
- `docs/STATE.md`
- `docs/HANDOFF.md`
- `docs/Q1_PLAN.md`
- `docs/RUNBOOK.md`

未修改：`A题/` 官方源、官方结果模板、`deliverables/candidate/`、`deliverables/final/`、`docs/CLAIMS.md`、`docs/ASSUMPTIONS.md`。

## Git Status

在本报告写入前，数值实现和实验脚本已提交；本报告及相关项目文档待本地文档提交。当前工作树不应包含未跟踪的官方源修改；提交前再次执行 `git status`、`git diff --check` 和 `pytest -q`。

## Commit SHA

- 实现与实验脚本提交：`843d62861b7137f93222f01df61609a228ceab5a` (`fix(q1): diagnose and improve numerical convergence`)
- 本轮文档提交：待提交后补记；不推送远端。

结论：`Q1 NUMERICAL REMEDIATION GATE BLOCKED`；`DO NOT GENERATE RESULT1`；`WAITING FOR HUMAN REVIEW`；`DO NOT START Q2`。
