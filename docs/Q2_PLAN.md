# Q2 Model Design & Contract Plan

> Gate：`CUMCM Q2 MODEL DESIGN & CONTRACT GATE`
>
> 当前状态：设计与契约已冻结为候选方案；Q2 implementation & short-horizon validation 已完成，未生成 `result2.xlsx`，Q3/Q4 未启动。

## 0. Current Project Status

| 项目 | 当前状态 |
|---|---|
| 当前问题 | Q2：整个烘干过程的温度与水分浓度场设计 |
| Q1 | `FROZEN / COMPLETE`；冻结提交 `a752e3a423dc48118b4bc8171c2a7bf9eb79f670`，本地标签 `q1-final` |
| Q2 | `IMPLEMENTATION & SHORT-HORIZON VALIDATION COMPLETE / WAITING LONG-HORIZON AUTHORIZATION` |
| Q3/Q4 | `NOT STARTED` |
| Q2 主模型 | `Q2-M1`：固定半径一维圆柱径向、变物性、温度–水分耦合模型；仅设计候选 |
| Q2 数值候选 | `Q2-NUM-CANDIDATE-A/B`；尚未选择最终方案 |
| Baseline | `Q2-B0`：冻结物性/简化控制模型；尚未运行 |
| 最好 Q2 实验 | `EXP-Q2-011`；0–10800 s内部验证完成，Candidate A BDF2 仅为推荐候选 |
| 已知失败/限制 | 团队 DOCX 无法用当前环境的 LibreOffice 做视觉渲染；正文与公式已用 `python-docx` 提取，并以官方 PDF 附录3复核公式；不影响官方源结论 |
| 当前阻塞 | 正式 `result2.xlsx`/长时全程仍需人工确认环境、界面平均、结束条件和精度门 |

## 1. Scope Boundary and Source Priority

本文件的主体记录 Q2 设计 Gate；以下实施范围由末尾 addendum 登记：Q2 solver、短时验证和0–3 h内部验证已完成。正式 2–3 天长时仿真、任何正式 Q2 交付数值结论、`result2.xlsx`、Q2 论文结论、Q3/Q4 实现仍不在当前授权范围。

来源优先级固定为：

1. 官方题面 `A题/A题.pdf`；
2. 官方附件 `A题/附件/`；
3. 已确认的人工决策；
4. 团队资料 `TEAM_REFERENCE`；
5. Agent 推断。

以下五个 DOCX 只作为 `TEAM_REFERENCE`，不能改变官方事实、不能覆盖官方公式、不能把建议数值写成论文结论：

- `D:\28045\Downloads\问题一解决步骤.docx`
- `D:\28045\Downloads\问题二解决步骤.docx`
- `D:\28045\Downloads\问题三解决步骤.docx`
- `D:\28045\Downloads\问题四解决步骤.docx`
- `D:\28045\Downloads\模型与数值方案总览.docx`

当前环境没有 `soffice.exe`，因此 DOCX 视觉渲染未完成；其文字和表格已抽取，DOCX 中可能损坏的公式不作为证据。附录3公式、单位和 Q2 输出要求已直接从官方 PDF 文本提取并对 PDF 页面 4 进行视觉核对。

## 2. Official Q2 Requirement Matrix

| 项目 | 官方要求 | 状态 | 来源/边界 |
|---|---|---|---|
| 目标 | 建立整个烘干过程中药材温度和水分浓度变化规律的模型 | `STATEMENT_FACT` | 官方 PDF 问题2 |
| 物性 | 使用附录3给出的 `ρ(C)`、`cp(C)`、`k(C)`、`D(C,T)` | `STATEMENT_FACT` | 官方 PDF 附录3 |
| 论文温度表 | 表3，`0.5,1.0,1.5,2.0,2.5,3.0 h`，半径 `0,0.5,1,1.5,2 cm` | `STATEMENT_FACT` | 官方 PDF 问题2/表3 |
| 论文水分表 | 表4，时间与半径同上 | `STATEMENT_FACT` | 官方 PDF 问题2/表4 |
| 完整结果 | `result2.xlsx`；时间每隔 `1 s`，径向距离每隔 `0.1 cm` | `STATEMENT_FACT` | 官方 PDF 问题2/附录3 |
| Sheet | `温度`、`水分浓度` | `STATEMENT_FACT` | 官方模板 |
| 输出单位 | 温度 `°C`；水分浓度 `kg/kg`；Excel 时间 `s`；论文表时间 `h`；距离 `cm` | `STATEMENT_FACT` | 官方 PDF 与模板 |
| 精度 | 最终输出四位小数 | `STATEMENT_FACT` | 官方题面 |
| 终点 | “整个烘干过程”未给出可直接写入 Q2 的数值终止行 | `OPEN_QUESTION` | 不把 Q3 的 `C<0.15` 自动写成 Q2 官方终点 |
| 内部网格 | 官方只规定完整输出空间采样，不规定内部求解网格 | `OPEN_QUESTION` | A/B 数值候选待验证 |
| 时间步 | 官方完整输出间隔为 `1 s`，内部步长/积分阶数未规定 | `OPEN_QUESTION` | 不把团队 `dt=1 s`升级为官方事实 |

## 3. Official Inputs and Data Catalog

| 资产 | 用途 | 保护/审计状态 |
|---|---|---|
| `A题/A题.pdf` | Q2 目标、表3/表4、附录3公式和单位 | 官方源，只读；SHA-256 `052d8014bff5727c019b72e44fdffaf5c145ce04050dd938baaf3527db331736` |
| `A题/附件/附件1.xlsx` | 烘房温度 `T∞(t)` 与水分浓度 `C∞(t)` 边界输入 | 官方源，只读；SHA-256 `7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7` |
| `A题/附件/附件3/result2.xlsx` | Q2 官方结果模板 | 官方源，只读；SHA-256 `23b261b295c1b787d000eebbca6521c37075107b6fcf78724f8d395ce1798ff4` |
| 附录2/问题1信息 | 初始场、几何和边界系数的 Q1 可复用输入 | 只按 Q1 已登记事实复用；若 Q2 物理含义改变必须重新登记 |

附件1结构审计：`Sheet1`，242 行 × 3 列，241 个数据点，时间 `0..14400 s`，相邻间隔均为 `60 s`，无空值、重复时间或非有限值。原始附件不清洗、不覆盖；输入处理只允许在 `data/interim/` 或运行时只读插值层完成。

## 4. `Q2_PROPERTY_SPEC`（官方附录3）

内部计算变量和单位必须显式写出：

| 符号 | 定义 | 内部单位 | 输出/输入说明 |
|---|---|---|---|
| `C` | 干基水分浓度 | `kg/kg` | 不做隐式百分数转换 |
| `T` | 药材绝对温度 | `K` | 输入 `°C` 后显式 `T_K=T_°C+273.15` |
| `ρ(C)` | 密度 | `kg/m^3` | 变量物性 |
| `cp(C)` | 比热容 | `J/(kg·K)` | 变量物性 |
| `k(C)` | 热传导系数 | `W/(m·K)` | 变量物性 |
| `D(C,T)` | 水分扩散系数 | `m^2/s` | 变量物性，要求 `C>0,T>0` |

官方公式：

```text
ρ(C)  = 650 + 128 C                         kg/m^3
cp(C) = 1450 + 2736 C/(C+1)                 J/(kg·K)
k(C)  = 0.21 + 0.38 C/(C+1)                W/(m·K)
D(C,T)= 2.4×10^-3 exp(-0.45/C) exp(-3850/T) m^2/s
```

公式点检设计（不是正式 Q2 结果）：

| 测试点 | 预期/已审计值 |
|---|---:|
| `C=2.55,T=301.15 K` | `ρ=976.4`，`cp=3415.295774647887`，`k=0.48295774647887324`，`D=5.641680373025664e-9` |
| `C=2.55,T=323.15 K` | `D=1.3470968217415811e-8`；与 `301.15 K` 的比值约 `2.387758137065687` |
| `C=1,T=323.15 K` | `ρ=778`，`cp=2818`，`k=0.4`，`D=1.024723031208691e-8` |
| `C=0.15,T=323.15 K` | `ρ=669.2`，`cp=1806.8695652173913`，`k=0.25956521739130434`，`D=8.001208146652626e-10` |
| 错把 `50°C` 直接代入 `T` | `D≈7.29e-37`，应由测试拒绝；这不是 Q2 数值结果 |

实现前的属性测试必须覆盖：已知点复算、`°C→K` 转换、有限性与正值、`C→0+` 的数值保护、随 `C`/`T` 的范围与单调性、公式单位注释和异常输入 fail-closed。所有中间计算保留完整精度，四舍五入只在交付生成层进行。

## 5. Q1 → Q2 Delta Matrix

| 维度 | Q1 冻结口径 | Q2 设计口径 | 变化分类 |
|---|---|---|---|
| Geometry | 一维圆柱径向，固定 `R=2 cm` | 同一固定半径一维径向候选 | `SAME` |
| Initial condition | `T=28°C`，`C=2.55 kg/kg` 均匀 | 作为 Q2 起始状态候选，需与全程分段环境接续核对 | `EXTENDED` |
| Heat equation | `ρ,cp,k` 为常数 | `ρ(C),cp(C),k(C)` 进入热方程 | `REPLACED` |
| Moisture equation | `D(C)` | `D(C,T)` | `REPLACED` |
| `ρ` | 常数 `820 kg/m³`（Q1） | `650+128C` | `REPLACED` |
| `cp` | 常数 `2600 J/(kg·K)`（Q1） | `1450+2736C/(C+1)` | `REPLACED` |
| `k` | 常数 `0.36 W/(m·K)`（Q1） | `0.21+0.38C/(C+1)` | `REPLACED` |
| `D` | `7e-9 exp(-0.89/C)` | `2.4e-3 exp(-0.45/C)exp(-3850/T)` | `REPLACED` |
| Boundary | 中心对称；表面热/质 Robin | 仍为候选中心对称与表面 Robin，参数/环境分段需复核 | `EXTENDED` |
| Environment | 附件1早期窗口内插值 | 附件1前段 + 14400 s 后常值或替代插值候选 | `EXTENDED` / `UNRESOLVED` |
| Nonlinearity | 水分单场非线性 | 温度–水分双场、变物性非线性 | `REPLACED` |
| Field coupling | Q1 设计中温度与水分不互相更新 | `C→ρ,cp,k`，`T,C→D`，必须耦合迭代 | `REPLACED` |
| Horizon | `0..1800 s` | 至少覆盖表3/4的 `0.5..3 h`；整个过程终点未冻结 | `EXTENDED` / `UNRESOLVED` |
| Output | Q1 `1..1800 s`，`0.1 cm` | Q2 每 `1 s`、每 `0.1 cm`，终点行未冻结 | `EXTENDED` |
| Solver reuse | `src/common`、`src/q1` 的网格/Thomas/单位/边界测试可复用 | 提取共享层前先回归 Q1，再做小规模 Q2 | `SAME` / `EXTENDED` |
| Numerical method | 冻结：聚簇保守 FVM、首步 BE + BDF2、`dt=.25 s` | 作为 Candidate A；另设 uniform+BE Candidate B | `EXTENDED` / `UNRESOLVED` |
| Validation | Q1 全时域 `<5e-5` 团队门已通过 | 重新验证长时累积误差、耦合、物性和重启；不自动继承 | `REPLACED` / `EXTENDED` |
| Deliverable | `result1.xlsx` 已冻结 | `result2.xlsx` 契约草案；终止时间和行数开放 | `EXTENDED` |

Q1 的生产配置只作为 Q2-NUM-CANDIDATE-A 输入，不是 Q2 官方要求；不得借 Q2 设计改写 Q1 结果、图表、冻结求解行为或生产配置。

## 6. Q2 Physics Candidate: `Q2-M1`

### 6.1 Governing fields

令 `r∈[0,R]`，`R=0.02 m`，`T(r,t)` 为 K，`C(r,t)` 为 kg/kg。当前主候选为固定半径、轴向均匀的圆柱径向模型：

```text
ρ(C) cp(C) ∂T/∂t = (1/r) ∂/∂r [ r k(C) ∂T/∂r ]
∂C/∂t           = (1/r) ∂/∂r [ r D(C,T) ∂C/∂r ]
```

候选边界：

```text
∂T/∂r(0,t) = 0                 ∂C/∂r(0,t) = 0
-k(C)∂T/∂r(R,t) = h[T(R,t)-T∞(t)]
-D(C,T)∂C/∂r(R,t) = hm[C(R,t)-C∞(t)]
```

初始场候选为 Q1 已登记的 `T(r,0)=28°C`、`C(r,0)=2.55 kg/kg`；执行时必须把 `T` 显式转为 `301.15 K`。`h=25 W/(m²·K)` 和 `hm=8×10^-7 m/s` 的延续来自 Q1/团队资料，属于需要复核的建模口径，不在本 Gate 升级为 Q2 官方新事实。

### 6.2 Coupling graph

```text
C ──► ρ(C), cp(C), k(C) ──► heat equation ──► T
T,C ────────────────────────► D(C,T) ────────► moisture equation ──► C
```

Q2 设计阶段不写“耦合很大”“温度一定加快干燥”或“某机制占主导”等结论；这些只能由后续实验和可追溯结果支持。

### 6.3 Control baseline `Q2-B0`

`Q2-B0` 作为可解释控制：保留相同几何、初边界和输出坐标，但冻结部分物性或采用简化的单向更新，用于定位“变物性”和“温度–水分反馈”的数值影响。B0 只用于对照，不替代 `Q2-M1`，也不在本 Gate 运行。

## 7. Environment Design and Open Questions

### `OQ-Q2-ENV-001`: 附件1结束后的环境

官方附件1到 `t=14400 s`。原始尾段审计（最后 40 个点，`12060..14400 s`）为：

| 量 | 均值 | 标准差 | 最后点 | 范围 | 线性趋势斜率 |
|---|---:|---:|---:|---:|---:|
| `T∞` (`°C`) | `49.99525` | `0.1558534` | `50.165` | `49.757..50.236` | `3.00094e-5 °C/s` |
| `C∞` (`kg/kg`) | `0.049988` | `0.0001374627` | `0.04986` | `0.04977..0.05024` | `-2.9143e-8 (kg/kg)/s` |

最后 10/20/40/80 点的统计已保存到 `experiments/EXP-Q2-ENV-TAIL/metrics.json`。团队建议在 `14400 s` 后采用常值 `T∞=50.00°C`、`C∞=0.0500`，但这是 `TEAM_REFERENCE_NUMERICAL_PROPOSAL`，不是官方事实；最后一点也不是该建议常值的证明。

候选处理：

- `ENV-A`：`0..14400 s` 原始点之间分段线性，之后从 `14400 s` 起常值；尾段常值采用团队建议，须人工确认。
- `ENV-B`：同样两阶段，但常值取尾窗统计量；这会把具体尾窗选择引入模型，须人工确认。

本 Gate 不选择 A/B，不把 `14400 s` 后值写入官方数据，也不运行长时仿真。

### `OQ-Q2-ENV-002`: 附件1内插值

设计比较 `ENV-INTERP-A` 分段线性与 `ENV-INTERP-B` PCHIP。两者都必须穿过原始数据点、不做全局多项式、不平滑或外推原始点。未来在 `0..3 h` 的论文时刻、早期内部场、表面 Robin 残差和输入曲线边界平滑性上做敏感性实验；当前不决定首选。

### `OQ-Q2-END-001`: “整个烘干过程”终点

Q2 官方明确了 `0.5..3 h` 论文展示，但未把 Q3 的“各处 `C<0.15 kg/kg`”写成 Q2 的官方结束条件。团队资料提出共享长时运行并观察 `C<0.15` 事件，作为 Q3 接口的工作流选项；这不是本 Gate 的 Q2 事实，也不在本 Gate 运行。需要人工决定：Q2 是否只交付题面明确的 3 h 展示 + 既定完整输出窗口，或是否授权一个覆盖 Q3 事件的共享长时内部轨迹。

### Other open questions

- `OQ-Q2-BC-001`：Q1 的 `h/hm` 是否原样延续 Q2，及其传质 Robin 的物理解释；候选敏感性为 ±10%，未决定。
- `OQ-Q2-FVM-001`：变系数界面 `k,D` 采用算术平均还是调和平均；团队仅提出算术平均，不是官方要求。
- `OQ-Q2-ACC-001`：Q1 的 `<5e-5` 团队门可作为候选起点，但必须检查长时累积误差、事件时刻敏感性、耦合迭代误差和运行成本后再冻结。

## 8. Q2 Numerical Candidate Matrix

| ID | Spatial | Time | Nonlinear coupling | 用途/状态 |
|---|---|---|---|---|
| `Q2-NUM-CANDIDATE-A` | Q1 冻结边界聚簇保守径向 FVM；base320 口径，实际约 339 节点；输出点并集保留 | 首步 BE，随后 BDF2；`dt=.25 s` 作为 Q1 复用候选 | 耦合 Picard / block Gauss–Seidel | 主候选，未实现、未选择 |
| `Q2-NUM-CANDIDATE-B` | uniform conservative radial FVM；团队建议 `Δr=.25 mm`，约 81 节点 | 全隐式 BE，`dt≈1 s` | 耦合 Picard / block Gauss–Seidel | 简洁对照，未实现、未选择 |
| `Q2-NUM-CANDIDATE-C` | 仅在 A/B 出现空间敏感性或边界层问题时比较 uniform/clustered 几何 | 由前两者诊断决定 | 同上 | 条件性诊断候选，不预先实现 |

暂不增加 Crank–Nicolson、高阶时间法、全 Newton 或 FEM；只有 A/B 无法通过验证时，才在新的 Level 3 授权下提出。

### 8.1 Coupled Picard design

未来实现必须逐步记录：

1. 第 `n+1` 步初值猜测为上一时间层 `T^n,C^n`；BDF2 时保留合法的前两层状态，首步仍使用 BE。
2. 采用 block Gauss–Seidel 顺序：先用当前 `C` 计算 `ρ,cp,k` 并求温度，再用最新的 `T` 和当前/最新 `C` 计算 `D` 并求水分。
3. 每一场更新后重新装配对应变系数；禁止把旧 `D`、旧 `k` 或摄氏温度直接跨迭代复用而不记录。
4. 分别计算温度残差 `e_T` 和水分残差 `e_C`，先按各自场的尺度、范数和参考量归一化，再合并判定；不能把 `K` 和 `kg/kg` 直接相加。
5. 候选收敛条件为 `max(e_T_norm,e_C_norm)<1e-8`，`max_iter=50`；这是团队候选和 Q1 经验值，不是已经冻结的 Q2 门。
6. 若振荡或不收敛，记录每场残差序列和最大发生位置，按预先配置的 under-relaxation 逐级降阶；达到最大迭代次数则 fail-closed，不能静默接受最后一次迭代。
7. 每个时间步记录迭代次数、最终两场残差、松弛因子、物性范围、边界残差和失败原因；重启时这些元数据必须进入 checkpoint/日志。

### 8.2 Variable-coefficient FVM audit

在面 `i+1/2` 处至少比较：

- 算术平均：`a_{i+1/2}=(a_i+a_{i+1})/2`；团队资料提出此方案，仅为 `TEAM_REFERENCE_NUMERICAL_PROPOSAL`。
- 调和平均：`a_{i+1/2}=2a_i a_{i+1}/(a_i+a_{i+1})`；在系数对比明显时作为守恒扩散候选。

未来 benchmark 必须检查离散守恒、常系数一致性、光滑变系数阶数、强梯度/正值边界情况和解对界面平均方式的敏感性；本 Gate 不预先选择算术平均。

## 9. Reusable Architecture (Interfaces Only)

Q2 计划复用 `src/common` 和 `src/q1` 的成熟组件，不复制 Thomas 求解、径向几何、单位转换、Robin 装配和 Q1 回归测试。计划中的文件边界如下，全部只是接口规划：

| 路径 | 计划职责 |
|---|---|
| `src/q2/properties.py` | 附录3物性函数、单位/域检查、属性测试接口 |
| `src/q2/environment.py` | 附件1只读加载、linear/PCHIP 候选和两阶段环境状态接口 |
| `src/q2/model.py` | Q2-M1 方程、边界和变系数装配接口 |
| `src/q2/solver.py` / `config.py` | A/B 候选配置、BE/BDF2、耦合 Picard 和 checkpoint 接口 |
| `src/q2/validation.py` | Q2 专用残差、守恒、极限、收敛和重启检查 |
| `src/q2/runner.py` | 流式输出、论文采样、断点续算和审计元数据 |

若未来必须抽取共享代码，顺序固定为：先建立 Q1 regression test → 做最小共享层抽取 → 全量 Q1 测试 → 再启用 Q2。不得为了 Q2 直接修改 Q1 冻结行为。

## 10. Long-Horizon Architecture

### 10.1 Storage and memory design

内部时间步不全部保存在内存。运行器应维护当前场、必要的历史层和小型诊断窗口；每个 `1 s` 输出点流式写入候选输出或分块中间文件，checkpoint 定期保存，最终再由已验证转换器写入从官方模板复制的 candidate。当前 Gate 不写任何工作簿。

若终止时间为 `t_end` 秒、按整数秒输出且暂不计额外事件行，则每个 Sheet 的数据行数约为 `N_rows=ceil(t_end)`（是否含 `t=0`、是否追加非整数终点仍是开放契约）。每行 `22` 列：时间 1 列 + `0..2 cm` 每 `0.1 cm` 的 21 个空间值；两 Sheet 总数约 `2×N_rows×22` 单元格。

规划估算（不是运行结果）：

- 72 h 安全窗口为 `259200 s`，对应约 `259200` 个整数秒数据行/Sheet；原始双精度数值仅按两场值估算为 `259200×21×2×8≈87.1 MB`，Excel XML/样式开销会更大。
- Candidate A 若沿用 Q1 的约 339 节点，当前 `T,C` 两个快照约 `5.3 KiB`；BDF2 保存两层历史约 `10.6 KiB`，尚不含矩阵、Picard 工作区和 Python 对象。故内存瓶颈应由流式输出解决，而不是缓存完整轨迹。
- 运行时间不能由 Q1 秒数线性外推为正式结论；计划在短时 pilot 中测量每步成本、Picard 平均迭代数和 A/B 因子，再用 `runtime≈步数×每步基准成本×耦合因子` 估算。无 pilot 前不宣称 2–3 天运行可行或不可行。

### 10.2 Checkpoint/restart contract

checkpoint 至少保存：物理时间、`T/C` 当前场与必要历史层、空间网格、完整 solver config、环境阶段/插值状态、官方输入哈希、代码 commit SHA、物性版本、输出游标、迭代诊断和写入块校验。未来必须比较连续运行与 checkpoint restart 的场、输出和诊断等价性，形成 `EXP-Q2-RESTART`；不允许不带版本和输入身份的“裸数组”重启。

### 10.3 Q2 → Q3 interface (design only)

只设计接口，不实现 Q3：事件观察器（全场 `C<0.15` 的候选判断）、采样策略、checkpoint 交接、流式结果块和环境状态都应能被 Q3 读取。Q2 不能把 Q3 阈值写成已经批准的 Q2 终点。

## 11. Validation Plan

未来实现至少登记以下检查；当前状态为设计项，不代表 Q2 已通过：

| 类别 | 检查 |
|---|---|
| Properties | 已知公式点、`°C/K` 转换、单位、有限/正值、域保护、范围和单调性 |
| Environment | 原始点重现、linear/PCHIP、两阶段 `14400 s` 转换、常值尾段、无未登记外推 |
| Limits | 常场不变、`D=0` 或 `hm=0` 水分不变、`h→∞` 热边界极限、中心对称 |
| Boundary | 热/质 Robin 离散残差、通量方向、中心零通量、表面控制体几何 |
| FVM | 常系数 benchmark、变量 `k` benchmark、变量 `D` benchmark、算术/调和平均比较 |
| Coupling | Picard 两场残差、迭代上限/松弛、物性更新时序、失败关闭行为 |
| Convergence | `dt` 收敛、空间/聚簇网格收敛、早期/表面层、长时累积误差 |
| Conservation | 固定半径总水分库存、表面通量积分、单步质量残差、累计质量残差 |
| Energy | 以离散热方程残差做能量检查；不能直接把 `Δ∫ρcpT` 当作 Q2 能量残差，因为 `ρ,cp` 随 `C` 变 |
| Cross-check | `EXP-Q2-Q1-OVERLAP` 只比较 `0..1800 s` 的 NaN、量级、中心/表面和界面行为；因物性不同不预期数值相等 |
| Reproducibility | 确定性、配置/输入 hash、checkpoint/restart 等价、重复运行输出 hash |
| Delivery | Sheet、轴、单位、四舍五入 `ROUND_HALF_UP`、完整性、模板来源和 candidate 隔离 |

固定半径总水分库存与表面通量积分的离散定义需与控制体体积一致；“干骨密度”解释沿用 Q1 已登记的模型假设时必须保留其非官方、可重审属性。

## 12. Q2 Deliverable Contract Draft (`Q2_DELIVERABLE_SPEC`)

本节是草案，不修改官方模板、不生成文件、不冻结终止行数。

| 项目 | 契约草案 |
|---|---|
| Source | 从 `A题/附件/附件3/result2.xlsx` COPY ONLY 到 `deliverables/candidate/result2.xlsx` |
| Sheets | `温度`、`水分浓度`，名称不可变 |
| Excel time | A 列为 `s`；完整结果每隔 `1 s`；是否含 `t=0`、是否追加终止事件行待确认 |
| Space | 第1行到中心距离 `0.0,0.1,...,2.0 cm`；完整输出每隔 `0.1 cm` |
| Values | 温度 `°C`，水分浓度 `kg/kg` |
| Precision | 最终写出四位小数，采用统一、可复现的 `ROUND_HALF_UP` |
| Paper Table 3 | `0.5,1,1.5,2,2.5,3.0 h` × `0,0.5,1,1.5,2 cm` |
| Paper Table 4 | 同上，变量为水分浓度 |
| End time | Q2“整个过程”的数值终点 `OPEN_QUESTION`；不把 Q3 `C<0.15` 直接冻结为 Q2 官方要求 |
| Shape | `OPEN_QUESTION`；不得按 5×6 模板骨架硬编码最终行数 |
| Validation | 结构、轴、有限值、单位、精度、来源 hash、论文点追踪、确定性和 candidate/final 隔离全部通过后才可申请人工确认 |
| Final promotion | 只有人工确认后，candidate 才能 COPY 到 `deliverables/final/`；本 Gate 不执行 |

## 13. Visualization Design Only

本阶段不生成正式 Q2 结果图或论文图。获得实现授权并通过数值验证后，候选可视化包括：径向温度/水分剖面、时空热图、中心/表面历史、中心–表面水分差、`ρ/cp/k/D` 物性演化和干燥速率诊断。每张图必须绑定输入 hash、solver config、源时间/空间采样和 experiment ID；在没有结果证据前，不写“外部已干而内部仍湿”“降速阶段”或“主导参数”等结论。

## 14. Risk Register

| 风险 | 影响 | 预防/验证 |
|---|---|---|
| 把 TEAM_REFERENCE 当官方要求 | 高 | 每条建议标注来源；官方 PDF/附件优先 |
| 把 `°C` 代入附录3的 `T` | 高 | 属性点检、单位测试、`T_K` 接口单一入口 |
| 温度–水分场旧式解耦 | 高 | Q2-M1 明确 Picard 双场更新和残差分离 |
| 变物性界面装配不守恒 | 高 | 算术/调和平均 benchmark、控制体通量审计 |
| 尾段环境选错 | 高 | 保留 ENV-001/002，尾窗统计和两阶段敏感性 |
| 终点/行数过早冻结 | 高 | `OQ-Q2-END-001`；契约保留 OPEN |
| 长时内存/Excel 过大 | 中 | 流式输出、分块、checkpoint，不缓存全场历史 |
| Q1 共享代码回归 | 高 | 抽取前后全量 Q1 regression；Q1 资产 hash 检查 |
| Picard 不收敛或静默接受失败 | 高 | max iteration、松弛策略、fail-closed、残差日志 |
| 精度门被错误继承 | 中 | 新建 Q2 长时累计误差和事件时刻敏感性门 |
| DOCX 公式渲染误读 | 中 | 不把 DOCX 公式当官方证据，以官方 PDF 页面4为准 |

## 15. Human Decisions Required

在 Q2 implementation authorization 前需确认：

1. `OQ-Q2-ENV-001`：`14400 s` 后采用团队 `50.00°C/0.0500` 常值，还是指定尾窗统计/其他规则？
2. `OQ-Q2-ENV-002`：`0..14400 s` 采用分段线性还是 PCHIP 作为主环境插值？
3. `OQ-Q2-BC-001`：Q1 的 `h/hm` 与 Robin 口径是否原样延续 Q2？
4. `OQ-Q2-FVM-001`：变系数界面选择算术还是调和平均？是否要求两者都进入正式敏感性？
5. `OQ-Q2-END-001`：Q2 是否只覆盖题面明示的 3 h 展示，或授权共享长时轨迹覆盖 Q3 事件观察？
6. `OQ-Q2-ACC-001`：是否以 Q1 `<5e-5` 为候选起点，并接受长时/耦合/运行成本复核后再冻结？
7. 是否批准先实现 A/B 两个数值候选及小规模 pilot；批准不等于批准生成 final `result2.xlsx`。

## 16. Gate Completion Checklist

- [x] 官方 Q2 目标、时间/空间/单位/精度/Sheet 要求提取并分层。
- [x] 附录3公式、变量单位和 `T` 为 K 已由官方 PDF 复核。
- [x] Q1 → Q2 delta matrix 已建立。
- [x] 五份团队 DOCX 已标为 `TEAM_REFERENCE`，并与官方来源分离。
- [x] 附件1尾段环境统计和两阶段 OQ 已登记。
- [x] Q2 终止条件未把 Q3 阈值升级为官方事实。
- [x] Q2-M1、Q2-B0、A/B/C 数值候选已设计；A/B 已在 implementation gate 中实现并比较，未冻结最终方案。
- [x] 耦合 Picard、变量系数 FVM、长时存储、checkpoint/restart 已设计。
- [x] 验证矩阵和 result2 契约草案已建立。
- [x] Q1 final、Q1 figures、冻结 solver behavior 和 `A题/` 未修改。
- [x] Q2 solver、短时/0–3 h内部验证已完成；正式 `result2.xlsx`、Q2最终论文结论、Q3/Q4均未开始。

`Q2 MODEL DESIGN & CONTRACT GATE COMPLETE`

`Q2 IMPLEMENTATION & SHORT-HORIZON VALIDATION COMPLETE / WAITING LONG-HORIZON AUTHORIZATION`

`Q1 = FROZEN`

`Q3 = NOT STARTED`

`Q4 = NOT STARTED`

## Q2 Implementation Gate Addendum (2026-09-11)

在收到人工 implementation authorization 后，设计中规划的 Q2 独立组件已实现并完成短时验证。实现文件为 `src/q2/properties.py`、`src/q2/environment.py`、`src/q2/model.py`、`src/q2/config.py`、`src/q2/solver.py`、`src/q2/validation.py` 和 `src/q2/benchmark.py`；测试和实验证据位于 `tests/test_q2_*.py` 与 `experiments/EXP-Q2-001/` 至 `EXP-Q2-011/`。

Candidate A 的 BDF2 只在 EXP-Q2-007 中记录为 `RECOMMENDED_FOR_Q2_FREEZE`，不是最终冻结方案。PCHIP、14400 s 后环境、h/hm、界面平均、Q2 终点和精度门仍是开放问题；0–3 h运行只使用 Attachment 1 范围内输入，没有实现 Q3 事件停止逻辑。此 addendum 不改变 Q2 设计阶段的官方源优先级和 `result2.xlsx` 保护规则。

## Q2 Long-Horizon Boundary & Production Config Gate Addendum (2026-09-11)

收到新的人工授权后，Q2 长时边界与生产配置门已执行完成。实现和证据脚本为 `src/q2/` 与 `scripts/run_q2_long_horizon.py`；正式产物位于 `experiments/EXP-Q2-012-ENVIRONMENT/` 至 `EXP-Q2-020-BASELINE/`。本 addendum 只更新执行状态和已验证证据，不把设计阶段的开放解释改写为官方事实。

### 执行配置

- 主数值候选：Candidate A，边界聚簇保守 FVM，BE 首步/BDF2，`n=80`，`dt=0.25 s`，linear，harmonic。
- 环境候选：ENV-A 使用附件1最后原始点在 `14400 s` 后常值；ENV-B 使用最后40点均值作为独立比较，不混入主候选结论。
- 长时阶段：`0–21600–86400–172800–259200 s`，即 6/24/48/72 h；保留 12 h checkpoint 作为重启和收敛观察点。
- 事件逻辑：`C<0.15 kg/kg` 仅作为 passive observer；不得作为 Q2 终止条件，也不得启动 Q3。
- 输出逻辑：内部双精度、逐秒官方空间节点采样、流式 CSV、checkpoint；当前不写 Excel，不复制官方 result2 模板。

### 证据边界

EXP-Q2-012–020 已覆盖环境尾段/插值、h/hm、界面平均、ENV-A/ENV-B 长时、低 `D(C,T)`、Picard、质量/热量/Robin、重启、收敛和 B0。长时 `dt=1/.5` 与 `n=20/40` 相对于 `n=80,dt=.25` 的数字是稳定性 proxy；正式短时时间/空间 observed order 仍分别引用 EXP-Q2-005/006，因为它们满足固定比较维度和更细 reference 契约。

主 ENV-A 输出在一次中断后的恢复操作中暴露了 append-only 重复风险。raw 文件未删除，recovered 文件按 `(time_s,radius_cm)` / `time_s` 键完成完整性验证并用于图和收敛比较；solver 已增加按 checkpoint 游标截断逻辑。该过程记录于 `docs/FAILURES.md`。

### 当前推荐与未决事项

数值上推荐 ENV-A last raw point 后常值、linear、arithmetic face mean、Q1-carried h/hm 和 Candidate A；但推荐状态为 `PENDING_HUMAN_APPROVAL`。`OQ-Q2-ENV-001/002`、`OQ-Q2-BC-001`、`OQ-Q2-FVM-001`、`OQ-Q2-END-001` 和 `OQ-Q2-ACC-001` 继续 OPEN。72 h 仅是内部稳定性窗口，不能据此冻结 Q2 官方终点/行数或生成 `result2.xlsx`。

`Q2 LONG-HORIZON BOUNDARY & PRODUCTION CONFIG GATE COMPLETE / WAITING FOR Q2 PRODUCTION & RESULT AUTHORIZATION`
