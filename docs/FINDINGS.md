# Findings

这里只记录经过数据或实验支持的重要发现。未经验证的想法应放入 `HYPOTHESES.md`。

## 发现索引

| ID | 发现 | 问题 | 证据 | 状态 |
|---|---|---|---|---|
| FIND-Q1-001 | Q1 M1 实现的烟雾、有限性、初值、时间单调性、边界方向和离散守恒检查通过 | Q1 | EXP-001、EXP-007 | SUPPORTED（限当前方程与配置） |
| FIND-Q1-002 | 时间步长从 `1 s` 细化到 `0.5 s`、再到 `0.25 s` 时，最终输出差异继续减小 | Q1 | EXP-003 | SUPPORTED（数值敏感性） |
| FIND-Q1-003 | 内部网格从 `N=40` 到 `80`、再到 `160` 时，关键输出差异减小；主网格 `N=80` 在本实验中稳定 | Q1 | EXP-004 | SUPPORTED（数值敏感性） |
| FIND-Q1-004 | Robin 与 Dirichlet 边界会造成显著不同的最终场，边界条件是高影响建模选择 | Q1 | EXP-005 | SUPPORTED（不等于选择已冻结） |
| FIND-Q1-005 | 分段线性与零阶保持输入的最终温度最大差异约 `0.178 K`，插值处理不能视为无影响 | Q1 | EXP-006 | SUPPORTED（需保留建模选择） |
| FIND-Q1-006 | 在 `C_ref=2.55 kg/kg` 下，M1 与 M2 的平均最终水分相差约 `0.003424 kg/kg`；M1、M2 和 B0 的比较可重复 | Q1 | EXP-002 | SUPPORTED（不用于单独冻结主模型） |
| FIND-Q1-007 | 当前测试的最细 M1 配置未在完整交付网格上达到四位小数全量稳定 | Q1 | EXP-Q1-FINAL-CONV | SUPPORTED（限测试配置；阻塞交付） |
| FIND-Q1-008 | 独立制造解验证支持当前径向 FVM 的二阶空间阶与 BE 一阶时间阶 | Q1 | EXP-Q1-NUM-BENCH | SUPPORTED（隔离 benchmark） |
| FIND-Q1-009 | 真实 Q1 空间误差的温度在表面/早期端部较明显，含水率 L∞ 主要集中在早期表面；BE 时间误差同样由早期/表面含水率主导 | Q1 | EXP-Q1-NUM-DIAG | SUPPORTED（限当前 M1） |
| FIND-Q1-010 | Picard 容差从 `1e-6` 收紧到 `1e-8`、`1e-10` 引起的场值变化远小于空间/时间离散差异 | Q1 | EXP-Q1-PICARD-SENS | SUPPORTED |
| FIND-Q1-011 | BDF2 候选显著改善论文 7×5 点时间稳定性，但完整网格含水率 Richardson 剩余误差仍超过 `0.5e-4` 四舍五入半单位 | Q1 | EXP-Q1-NUM-REMEDIATION | SUPPORTED（候选未冻结） |
| FIND-Q1-012 | t=0 温度场与温度 Robin 表示相容，而均匀初始水分场与表面水分 Robin 条件不相容；短时表面误差随后衰减，支持初始表面层诊断 | Q1 | EXP-Q1-INITIAL-LAYER、EXP-Q1-SURFACE-DECAY | SUPPORTED（数值诊断，不是模型错误判定） |
| FIND-Q1-013 | 边界聚类保守 FVM 在独立制造解 benchmark 中保持近二阶空间/一阶时间趋势，并显著降低真实 Q1 早期表面空间差异 | Q1 | EXP-Q1-CLUSTER-BENCH、EXP-Q1-CLUSTER-SHORT | SUPPORTED（候选未冻结） |
| FIND-Q1-014 | 早期 BE 子步启动没有显示出相对标准 BE 首步的稳定改善 | Q1 | EXP-Q1-BDF2-STARTUP | SUPPORTED（当前 M1-NUM-T2 对照范围） |
| FIND-Q1-017 | r=1.9 cm 的早期表面误差谷值由 signed error 穿零造成；字面 r=2.0 cm 表面无穿零，且空间细化时谷值移动而全局 L∞/L2 下降 | Q1 | EXP-Q1-SURFACE-DECAY、EXP-003、EXP-004 | SUPPORTED（pointwise error zero-crossing / cancellation dip；不得作为突然提速证据） |
| FIND-Q2-001 | 附录3变物性、单位和 Kelvin 输入测试通过 | Q2 | EXP-Q2-PROPERTY-POINTS、tests/test_q2_properties.py | SUPPORTED（属性实现范围） |
| FIND-Q2-002 | 变量系数 benchmark 的当前 Robin 节点闭合约一阶空间、BE约一阶时间 | Q2 | EXP-Q2-003 | SUPPORTED（隔离数值证据） |
| FIND-Q2-003 | 已运行短时和3小时配置的 coupled Picard 全部收敛且诊断完整 | Q2 | EXP-Q2-001、004、009、011 | SUPPORTED（实现状态，不是物理结论） |
| FIND-Q2-004 | 固定非比较维度的时间/空间细化误差均下降 | Q2 | EXP-Q2-005、EXP-Q2-006 | SUPPORTED（数值敏感性） |
| FIND-Q2-005 | Candidate A BDF2 在当前短时 accuracy proxy 中优于 BE，但仅推荐不冻结 | Q2 | EXP-Q2-007 | SUPPORTED（RECOMMENDED_FOR_Q2_FREEZE） |
| FIND-Q2-006 | checkpoint/restart 测试配置下逐点复现 | Q2 | EXP-Q2-010 | SUPPORTED（当前版本/配置） |
| FIND-Q2-007 | 0–3 h内部运行未触发14400 s后外推或Q3事件逻辑 | Q2 | EXP-Q2-011 | SUPPORTED（范围边界） |
| FIND-Q2-008 | ENV-A 候选完成0–72 h且低含水率物性/残差保持有限 | Q2 | EXP-Q2-016-A | SUPPORTED（数值稳定性，不是物理或交付批准） |
| FIND-Q2-009 | post-14400 s 环境规则会改变长时场 | Q2 | EXP-Q2-012、EXP-Q2-018 | SUPPORTED（环境选择仍 OPEN） |
| FIND-Q2-010 | linear/PCHIP 非等价，而 arithmetic/harmonic 在当前真实运行差异很小 | Q2 | EXP-Q2-013、EXP-Q2-015 | SUPPORTED（选择仍待人工冻结） |
| FIND-Q2-011 | 长时收敛无失控、重启一致且 B0 仅为有限成本控制 | Q2 | EXP-Q2-017、019、020 | SUPPORTED（proxy/控制证据） |
| FIND-Q2-012 | ENV-A 与 tail40 的长时差异不可忽略 | Q2 | EXP-Q2-018 | SUPPORTED（环境仍待冻结） |
| FIND-Q2-013 | Linear 与 PCHIP 不是数值等价替换 | Q2 | EXP-Q2-013 | SUPPORTED |
| FIND-Q2-014 | hm 对被动阈值时刻比 h 更敏感 | Q2 | EXP-Q2-021 | SUPPORTED（targeted screen） |
| FIND-Q2-015 | 长时 arithmetic/harmonic 差异不能按短时结果冻结 | Q2 | EXP-Q2-015、021 | SUPPORTED |
| FIND-Q2-016 | Recovered canonical loader 已阻断 raw duplicate 消费 | Q2 | manifest、lineage guard、tests | SUPPORTED |

## 发现记录模板

```markdown
## FIND-xxx 标题

问题：Q1/Q2/Q3/Q4
发现：
证据：EXP-xxx 或明确的数据分析结果
适用范围：
限制：
对模型/论文的影响：
状态：SUPPORTED / OUTDATED
```

## FIND-Q1-001 Q1 实现与运行检查通过

问题：Q1

发现：M1 在短时 smoke 和完整 1800 s 配置下均保持有限；初值、时间序列、Robin 边界方向、质量残差、常物性储热残差和水分非负性检查通过。EXP-001 的质量残差为 `3.64e-20`，EXP-007 的质量残差为 `-5.42e-20`、能量残差为 `1.13e-7`。

证据：`experiments/EXP-001/metrics.json`、`experiments/EXP-007/metrics.json`

适用范围：当前 `N=80`、`dt=1 s`、线性插值、Robin 边界和未加入潜热/交叉耦合的 Q1 候选方程。

限制：这些检查验证数值实现和当前方程的内部一致性，不证明被省略的物理效应不存在，也不构成论文结论。

状态：SUPPORTED

## FIND-Q2-012 ENV-A 与 tail40 的长时差异不可忽略

问题：Q2

发现：在相同 `n=80, dt=.25 s` 和相同 solver 配置下，ENV-A last raw 与 ENV-B tail40 mean 在 6/24/48/72 h 的温度 L∞ 分别为 `0.169486/0.169750/0.169750/0.169750 °C`，水分 L∞ 分别为 `0.0014492/0.0007154/0.0003763/0.0002776 kg/kg`；passive bracket 从 `205913–205913.25 s` 移至 `207034.5–207034.75 s`。

证据：`experiments/EXP-Q2-018-ENV-COMPARISON/metrics.json`、`docs/Q2_HUMAN_DECISION_PACKET.md`。

适用范围：当前固定半径 Q2-M1、ENV-A/B 后常值规则；不等同于官方终点或 Q3 答案。

状态：SUPPORTED；环境选择仍需人工冻结。

## FIND-Q2-013 Linear 与 PCHIP 不是数值等价替换

问题：Q2

发现：两种插值都精确经过附件1原始 knots，但在 Table 3/4 五个官方半径的纸面点上，0–3 h 温度最大差为 `2.3889714e-3 °C`、水分最大差为 `7.9729742e-6 kg/kg`；0–4 h 全节点最大差为 `8.9368847e-3 °C`、`1.6431732e-5 kg/kg`。

证据：`experiments/EXP-Q2-013-INTERPOLATION/metrics.json`、其 `samples_linear.csv`/`samples_pchip.csv`。

状态：SUPPORTED；不能因实现简单而把二者写成等价。

## FIND-Q2-014 hm 对被动阈值时刻比 h 更敏感

问题：Q2

发现：±10% h 在 targeted 72 h screen 中只造成约 `4.9–6.0e-6 kg/kg` 的 moisture L∞，passive bracket 位移为 `-26/+32 s`；±10% hm 造成约 `3.94–5.10e-4 kg/kg` 的 moisture L∞，bracket 位移为 `-2076/+2646 s`。

证据：`experiments/EXP-Q2-021-DECISION-TARGETS/boundary_long_target_metrics.json`。

限制：targeted screen 使用 `dt=2 s`，用于边界假设影响诊断，不替代 production accuracy gate；bracket 仍是 passive diagnostic。

状态：SUPPORTED；h/hm 仍是 carried-forward modeling assumptions。

## FIND-Q2-015 长时 arithmetic/harmonic 差异不能按短时结果冻结

问题：Q2

发现：manufactured benchmark 与 0–3 h 实际 Q2 对照均通过；但同一 canonical 时空配置下，arithmetic 相对 harmonic 的 moisture L∞ 在 24/48/72 h 为 `1.3957089e-4/1.2652593e-4/1.0147461e-4 kg/kg`，高于 packet 拟议的 `2.5e-5` field gate，因此当前证据支持保留 harmonic，而不支持直接冻结 arithmetic。

证据：`experiments/EXP-Q2-015-INTERFACE-MEAN/metrics.json`、`experiments/EXP-Q2-021-DECISION-TARGETS/interface_long_target_metrics.json`。

状态：SUPPORTED；界面平均仍需人工决定。

## FIND-Q2-016 Recovered canonical loader 已阻断 raw duplicate 消费

问题：Q2

发现：主长时 run 的 raw sample 有 `97104` 个重复 rows、raw diagnostic 有 `4624` 个重复 keys；recovered files 完整且通过 SHA-256 manifest guard。`canonical_path/canonical_csv_path` 对非 canonical status fail-closed。

证据：`experiments/Q2_CANONICAL_DATA_MANIFEST.json`、`src/q2/lineage.py`、`tests/test_q2_lineage.py`。

状态：SUPPORTED；manifest 本身及生产配置仍等待人工冻结。

## FIND-Q2-001 附录3变物性实现与单位测试通过

问题：Q2

发现：实现严格采用官方 PDF 附录3的 `rho(C)`、`cp(C)`、`k(C)` 和 `D(C,T_K)`；已知点、正值/有限性、`C`/`T_K` 变化和摄氏误传保护测试通过。`T` 只在显式摄氏转 Kelvin 后进入 `D`。

证据：`src/q2/properties.py`、`tests/test_q2_properties.py`、`experiments/EXP-Q2-PROPERTY-POINTS/metrics.json`。

适用范围：Q2-M1 属性函数；不代表整个 Q2 物理模型已经被实验验证。

状态：SUPPORTED

## FIND-Q2-002 变量系数 benchmark 显示当前 Robin 节点闭合约一阶空间、BE 一阶时间

问题：Q2

发现：独立制造解同时测试变量径向热扩散和水分扩散。当前“表面节点 + Robin 半控制体”实现的全局空间 observed order 约为 `1.01–1.04`，BE 时间 observed order 约为 `1.00–1.16`。这与当前离散闭合相符；没有把空间二阶假设写成结果。

证据：`experiments/EXP-Q2-003/metrics.json`、`src/q2/benchmark.py`。

限制：这是制造解和当前边界闭合的数值证据，不是对真实 Q2 场的精度保证；界面平均主方案仍为开放数值决策。

状态：SUPPORTED

## FIND-Q2-003 Q2 coupled Picard 在已运行短时和3小时范围内收敛

问题：Q2

发现：0–60 s、0–300 s 和0–10800 s 的已运行配置均完成；每步分别记录温度/水分归一化 Picard 残差、迭代历史、线性残差、性质范围、Robin 通量差和离散质量/热量残差。0–3 h 运行的 Picard 迭代统计为 `min/median/p95/max=2/2/3/3`。

证据：`experiments/EXP-Q2-001/metrics.json`、`experiments/EXP-Q2-004/metrics.json`、`experiments/EXP-Q2-009/metrics.json`、`experiments/EXP-Q2-011/metrics.json`。

限制：这只支持实现与数值收敛状态；不支持“温度一定加快干燥”或其他物理机制结论。

状态：SUPPORTED

## FIND-Q2-004 时间与空间细化在指定短时验证中均下降

问题：Q2

发现：时间审计固定 uniform `dr=0.025 cm`，以 `dt=0.03125 s` 为 reference；`dt=1,.5,.25,.125 s` 的温度和水分 L∞/L2 误差均下降，observed order 进入约一阶区间。空间审计固定 `dt=.125 s`，`dr=.1,.05,.025 cm` 相对 `.0125 cm` reference 的温度和水分 L∞/L2 均下降，且比较按相同物理半径而不是相同数组索引进行。

证据：`experiments/EXP-Q2-005/metrics.json`、`experiments/EXP-Q2-006/metrics.json`。

限制：这些是0–1800 s数值敏感性结果；不关闭 Q2 终点、环境尾段或正式输出契约开放项。

状态：SUPPORTED

## FIND-Q2-005 BDF2 在当前 Candidate A 短时 accuracy proxy 中优于 BE，但不是 FINAL

问题：Q2

发现：在0–600 s共同配置比较中，Candidate A 的 BDF2 相对 BE 的温度 L∞ proxy 从 `3.2642e-4 K` 降至 `5.2822e-5 K`，水分 proxy 从 `1.1303e-3` 降至 `3.7759e-4`；因此实验记录为 `RECOMMENDED_FOR_Q2_FREEZE`，没有写成 FINAL。

证据：`experiments/EXP-Q2-007/metrics.json`。

限制：Candidate B 的表现不同；最终界面平均、精度门和 Q2 交付冻结仍待人工决定。

状态：SUPPORTED

## FIND-Q2-006 checkpoint/restart 在测试配置下逐点复现

问题：Q2

发现：0–600 s 运行在300 s保存 `Q2_CHECKPOINT_V1` 后重启，末场温度最大差值为 `0` K、水分最大差值为 `0`；checkpoint 同时保存网格、配置、历史层、Attachment 1 哈希和代码 commit SHA。

证据：`experiments/EXP-Q2-010/metrics.json`、`experiments/EXP-Q2-010/checkpoint.json`。

适用范围：该测试配置与当前实现版本；不是跨版本重启承诺。

状态：SUPPORTED

## FIND-Q2-007 0–3 h 实现运行未触发未批准的环境外推

问题：Q2

发现：Candidate A 的0–10800 s运行完成，所有时间均在 Attachment 1 的 `0..14400 s` 数据范围内；未启用14400 s后的常值 provider，没有实现 Q3 结束事件，也没有生成 `result2.xlsx`。运行性质范围、Picard统计和纸面时刻候选已保存。

证据：`experiments/EXP-Q2-011/metrics.json`、`experiments/EXP-Q2-011/diagnostics.csv`。

限制：这不是“整个烘干过程”已完成的物理结论；Q2终点开放问题仍保持 OPEN。

状态：SUPPORTED

## FIND-Q1-015 全时域边界聚簇 BDF2 配置通过团队数值门

问题：Q1

发现：在保持 Q1 M1 物理方程、Robin 边界、原始初值、附件1线性插值和非线性 `D(C)` 不变的条件下，边界聚簇保守径向 FVM（cluster power `2`）配合首步 BE、随后固定步长 BDF2，通过了完整 `1..1800 s × 0.0..2.0 cm` 的 3 层空间/3 层时间收敛门。最低成本通过配置为 base320（实际 338 个空间区间）、`dt=0.25 s`；温度最大估计不确定度为 `1.4012175e-6 °C`，含水率最大估计不确定度为 `2.7414225e-5 kg/kg`，两者均小于团队标准 `5e-5`。

证据：`experiments/EXP-Q1-FULL-SPATIAL/metrics.json`、`experiments/EXP-Q1-FULL-TEMPORAL/metrics.json`、`experiments/Q1_FREEZE_RUN/metrics.json`

适用范围：Q1 当前冻结配置、完整 `1800×21` 正式输出网格和论文 `7×5` 追踪点；数值标准是 `TEAM_NUMERICAL_CRITERION`，不是官方题面要求。

限制：局部 Richardson 阶数病态点使用登记的原始相邻细层差值包络；四位小数歧义仅作辅助诊断。该发现不证明物理模型误差为零，也不替代人工批准。

状态：SUPPORTED_PENDING_HUMAN_APPROVAL

## FIND-Q1-016 Q1 冻结运行与候选溯源可重复

问题：Q1

发现：`Q1_FREEZE_RUN` 按同一配置从零运行两次，两个包含完整内部时间层和空间节点的压缩输出参考 SHA-256 完全一致；两个运行的有限性、范围、Picard、质量/能量离散平衡检查均 PASS。候选 `deliverables/candidate/result1.xlsx` 只由 `run_1` 冻结参考生成；固定随机种子的 20 个单元格和温度/含水率两张论文表各 `35/35` 个点均逐点追踪通过。

证据：`experiments/Q1_FREEZE_RUN/metrics.json`、`experiments/Q1_FREEZE_RUN/validation.json`、`experiments/Q1_FREEZE_RUN/candidate_trace.json`、`experiments/Q1_FREEZE_RUN/candidate_validation.json`

限制：candidate 仍不是 final；需要人工 Q1 冻结批准后才可复制到 `deliverables/final/`。Q2/Q3/Q4 未启动。

状态：SUPPORTED_PENDING_HUMAN_APPROVAL

## FIND-Q1-012 Q1 初始水分层与表面 Robin 条件不相容

问题：Q1

发现：当前数值困难主要由初始水分场与表面 Robin 条件不相容产生的短时表面边界层导致。t=0 温度 Robin 残差为 `-0.0 W/m²`，而水分 Robin 残差为 `-2.024296e-6 m/s`，初始场与环境的水分跳跃为 `2.53037 kg/kg`。均匀网格 N640→N1280 的 r=2.0 cm 误差在 t=1 s 为 `3.0796e-4 kg/kg`，t=100 s 降为 `2.1780e-5 kg/kg`，前后比值约 `14.14`；后期空间观测阶回到约 `2`。

证据：`experiments/EXP-Q1-INITIAL-LAYER/metrics.json`、`experiments/EXP-Q1-SURFACE-DECAY/metrics.json` 及 `surface_moisture_error_decay.svg`。

适用范围：当前 M1、均匀初始水分场、Robin 表面边界、0–100 s 诊断窗口。

限制：这是数值相容性和误差分布证据，不证明物理模型错误；不得据此修改官方初始条件或强行改成 Dirichlet 边界，也不能外推为完整 1800 s 交付已通过。

状态：SUPPORTED

## FIND-Q1-013 边界聚类候选降低早期表面空间差异

问题：Q1

发现：独立制造解 benchmark 的边界聚类保守 FVM 空间 L∞ 观测阶约 `1.95–1.96`，时间 L∞ 观测阶约 `1.01–1.06`。真实 Q1、共同 `dt=0.0625 s` 下，均匀 N320→N640 的 t=1 s 表面差为 `1.3891e-3 kg/kg`，聚类 base640→base1280 的对应差为 `3.6753e-6 kg/kg`。聚类网格通过显式节点并集保留了 `0,0.001,...,0.020 m` 全部官方输出位置。

证据：`experiments/EXP-Q1-CLUSTER-BENCH/metrics.json`、`experiments/EXP-Q1-CLUSTER-SHORT/metrics.json`、`src/common/numerics.py`、`src/q1/model.py`。

适用范围：聚类幂 `p=2` 的当前候选和 0–10 s 窗口。

限制：聚类 base640/base1280 与均匀 N1280 的跨网格族差异不能直接当作误差估计；该短时发现已由独立的 `EXP-Q1-FULL-SPATIAL` / `EXP-Q1-FULL-TEMPORAL` 全时域验证补充，生产冻结仍需人工批准。

状态：SUPPORTED

## FIND-Q1-014 早期 BE 子步未显示改善

问题：Q1

发现：在 N640、正常步长 `0.25 s` 下，将 0–1 s 改为 BE 子步并重新启动 BDF2，与标准“第一步 BE、随后 BDF2”比较时，启动子步 `0.25/0.125/0.0625 s` 的标准/早期最大差异分别为 `9.3725e-4`、`9.9496e-4`、`1.5769e-3 kg/kg`；t=1 s 表面对同一高精度标准参考的早期子步值没有显示单调改善。

证据：`experiments/EXP-Q1-BDF2-STARTUP/metrics.json`。

适用范围：M1-NUM-T2、N640、0–10 s 对照窗口。

限制：不能据此证明其他启动策略在全时段都无效；当前只决定不把早期子步直接冻结为生产策略。

状态：SUPPORTED

## FIND-Q1-017 早期表面误差谷值是 signed-error zero-crossing

问题：Q1

发现：本轮重新审计后，表面误差明确保存为 `e(t)=C_test(R,t)-C_ref(R,t)` 和 `E(t)=abs(e(t))` 两列。N640（test）与 N1280（reference）在共同 `dt=0.0625 s` 下的 r=1.9 cm 数据中，20/25/30/35/40 s signed error 分别为 `-3.771722694612123e-06`、`-2.9872553728438334e-06`、`-1.6189237888042385e-06`、`-7.767662335567138e-08`、`+1.4272639048407143e-06`；35–36 s 发生符号改变，线性穿零估计为 `35.252150792027635 s`。因此绝对误差从约 `1e-6` 进入 `1e-8` 的深谷定性为 `pointwise error zero-crossing / cancellation dip`，不定性为算法精度突然提高两个数量级。字面 r=2.0 cm 表面在 15–45 s signed error 始终为正，没有对应穿零。

独立的固定 `dt=0.0625 s` 空间审计中，r=1.9 cm 相对于 `dr=0.0125 cm` reference 的穿零/谷值随 `dr=0.1/0.05/0.025 cm` 移动，穿零约为 `43.817/40.089/37.124 s`；对应的全局 L∞/L2 均下降。固定 `dr=0.025 cm` 的时间审计中，相邻 dt 直接差分的 L∞ observed order 为：表面 `0.929、0.962`，r=1.5 cm `0.998、0.999`，r=1.0 cm `0.999、1.000`，中心 `1.010、1.005`，符合 BE 进入渐近区后大致一阶的判断。

证据：`experiments/EXP-Q1-SURFACE-DECAY/metrics.json`、`experiments/EXP-Q1-SURFACE-DECAY/surface_signed_error_15_45s.csv`、`experiments/EXP-003/metrics.json`、`experiments/EXP-004/metrics.json`。

适用范围：当前 Q1 M1 uniform-grid BE 诊断；表面短时比较为 N640/N1280、共同 `dt=0.0625 s`，收敛审计 reference 分别为 `dt=0.0625 s` 和 `dr=0.0125 cm`。

限制：r=1.9 cm 是靠近表面的输出节点，不等同于字面 r=2.0 cm 表面；局部点态穿零不代表整个时间区间误差变小，也不改变 Q1 冻结生产配置或 final workbook。

对模型/论文的影响：禁止把 20–40 s 的绝对误差深谷写成模型优越性、快速收敛或算法精度突然提高的证据；如需描述，应使用 cancellation dip 的定性。

状态：SUPPORTED

## FIND-Q1-008 独立制造解支持空间/时间阶数

问题：Q1

发现：隔离制造解 `u(r,t)=e^{-t}(1+r^4)`、常扩散系数和 Robin 环境边界下，当前径向 FVM 的 BE 空间 L∞ 观测阶为 `1.9715, 1.9938, 1.9985`，BE 时间 L∞ 观测阶为 `1.0096, 1.0146, 1.0089`；中心和表面指标也保持相同趋势。该结果支持中心半体积、内部几何、表面 Robin 行和 Thomas 求解器的离散阶数符合预期。

证据：`experiments/EXP-Q1-NUM-BENCH/metrics.json`、`tests/test_q1_robin_boundary.py`

适用范围：独立 benchmark；不代表真实 Q1 物理误差或论文误差已经满足交付门。

限制：BDF2 benchmark 的后续细化已受到空间误差底影响，不能仅以其非单调 L∞ 阶判定生产候选失败。

状态：SUPPORTED

## FIND-Q1-009 Q1 误差定位在早期/表面含水率最显著

问题：Q1

发现：真实 Q1 的 N160→N320 空间比较中，温度 L∞ 最大值为 `2.2996e-5 °C`，发生于 `t=300 s,r=2.0 cm`；含水率 L∞ 最大值为 `0.0056513 kg/kg`，发生于 `t=1 s,r=2.0 cm`，且表面带 `r≥1.8 cm` 占平均绝对误差总量约 `76.6%`。BE 的 `dt=0.5→0.25 s` 时间比较中，温度 L∞ 为 `4.7762e-4 °C`、最大点 `t=897 s,r=0`；含水率 L∞ 为 `0.0011657 kg/kg`、最大点 `t=1 s,r=2.0 cm`，表面带占比约 `63.7%`。

证据：`experiments/EXP-Q1-NUM-DIAG/metrics.json` 及四张误差定位 SVG 图。

适用范围：M1、Robin、线性输入、完整 `1..1800 s × 0.0..2.0 cm` 比较。

限制：定位结果是误差分布证据，不等价于已确认边界物理错误；应先结合 benchmark 和边界单元测试审查。

状态：SUPPORTED

## FIND-Q1-010 Picard 迭代误差可忽略

问题：Q1

发现：300 s、N=160、dt=0.25 s 的敏感性运行中，Picard 容差分别为 `1e-6/1e-8/1e-10` 时最大迭代次数为 `2/3/4`；`1e-6` 对 `1e-8` 的温度 L∞ 差为 `0`、含水率 L∞ 差为 `1.5853e-9 kg/kg`，`1e-8` 对 `1e-10` 的含水率 L∞ 差为 `1.7009e-13 kg/kg`，均远小于生产空间/时间差异。

证据：`experiments/EXP-Q1-PICARD-SENS/metrics.json`

适用范围：当前 M1 非线性扩散、300 s 短验证配置。

限制：不替代完整 1800 s 结果的离散收敛检查，但支持将 Picard 容差排除为当前主要误差源。

状态：SUPPORTED

## FIND-Q1-011 BDF2 改善论文点但未通过完整网格安全门

问题：Q1

发现：M1-NUM-T2 使用一阶 BE 启动后切换 BDF2，保持相同物理模型、空间 FVM 和 Picard 设置。在 `N=320` 的 `dt=0.5→0.25 s` 比较中，论文 7×5 点温度和含水率均为 `0/35` 个四位小数差异；对应论文点 Richardson 剩余估计分别为 `4.6111e-7 °C` 和 `1.2677e-7 kg/kg`。但全网格含水率 L∞ 差为 `0.0011151 kg/kg`，观测阶约 `1.4902`，Richardson 剩余估计 `0.0006163 kg/kg`，不能冻结为最终方法。

证据：`experiments/EXP-Q1-NUM-REMEDIATION/metrics.json`、`experiments/EXP-Q1-NUM-BENCH/metrics.json`

适用范围：当前 Q1 M1 的时间积分候选；BDF2 仅为候选，不改变已冻结的交付契约。

限制：不能把论文点稳定性外推到完整网格，也不能将 BDF2 的候选结果直接写入 `result1.xlsx`。

状态：SUPPORTED

## FIND-Q1-007 最终交付网格四位小数稳定性尚未达到

问题：Q1

发现：在固定 M1 方程和当前参数下，空间细化 `N=80/160/320`、时间细化 `dt=1/0.5/0.25 s` 均已实际比较；最细空间比较 N160→N320 在完整 `1800×21` 网格仍有温度 `1398/37800`、水分 `4468/37800` 个四位小数变化，最细时间比较 dt1→dt0.25 仍有温度 `36498/37800`、水分 `6926/37800` 个变化。

证据：`experiments/EXP-Q1-FINAL-CONV/metrics.json`

适用范围：M1、一维径向 FVM、隐式 Backward Euler、Robin 边界、线性输入插值、完整 `1..1800 s × 0.0..2.0 cm` 网格，以及论文 7×5 追踪点。

限制：这是当前测试配置的输出级精度结果，不等同于模型方程或实现已被证明错误；不得据此修改论文核心结论，也不得在没有新决策的情况下放宽门槛。

对模型/论文的影响：Q1 candidate `result1.xlsx` 暂不生成；任何最终数值和论文表格均保持未确认状态。

状态：SUPPORTED

## FIND-Q1-002 时间步长细化的差异减小

问题：Q1

发现：`dt=1 s` 对 `dt=0.5 s` 的最终输出最大差异为 `0.000600 K` 和 `4.40e-5 kg/kg`；`dt=0.5 s` 对 `dt=0.25 s` 的差异降为 `0.000300 K` 和 `2.20e-5 kg/kg`。

证据：`experiments/EXP-003/metrics.json`

适用范围：M1、`N=80`、线性插值、Robin 边界、1800 s 终点场。

限制：这是终点输出敏感性，不替代完整时间序列误差分析。

状态：SUPPORTED

## FIND-Q1-003 空间网格细化的差异减小

问题：Q1

发现：`N=40` 对 `N=80` 的最终输出最大差异为 `5.32e-5 K` 和 `5.68e-4 kg/kg`；`N=80` 对 `N=160` 的差异降为 `1.33e-5 K` 和 `1.41e-4 kg/kg`。

证据：`experiments/EXP-004/metrics.json`

适用范围：`dr=0.5/0.25/0.125 mm`、`dt=1 s`、M1、1800 s 终点场。

限制：尚未完成端部效应或二维模型验证；该发现只支持当前一维径向离散的网格稳定性。

状态：SUPPORTED

## FIND-Q1-004 边界条件是高影响选择

问题：Q1

发现：在相同输入和内部网格下，Robin 与 Dirichlet 最终输出的最大温度差异为 `4.727 K`，最大水分差异为 `1.477 kg/kg`；Robin 方案的守恒/范围检查通过。

证据：`experiments/EXP-005/metrics.json`

适用范围：Dirichlet 仅作为 M3 敏感性对照；不据此宣称哪一种边界已被官方确认。

限制：`hm` 直接作用于干基浓度的解释仍是 `TEAM MODELING INTERPRETATION`，等待 OQ-006 人工决定。

状态：SUPPORTED

## FIND-Q1-005 输入插值处理不能视为无影响

问题：Q1

发现：同一附件1原始点下，分段线性与零阶保持输入的最终输出最大温度差异为 `0.1778 K`，最大水分差异为 `1.02e-4 kg/kg`。

证据：`experiments/EXP-006/metrics.json`

适用范围：`dt=1 s`、`N=80`、Robin 边界、1800 s 终点场。

限制：两种处理都没有平滑、删除或外推；最终默认插值方案仍需 Result Gate 确认。

状态：SUPPORTED

## FIND-Q1-006 M1/M2/B0 对照可重复

问题：Q1

发现：在 `C_ref=2.55 kg/kg` 的 M2 配置下，M1 与 M2 最终体积加权平均水分分别为 `2.293482` 与 `2.290058 kg/kg`，差异约 `0.003424 kg/kg`；B0 平均水分为 `2.211596 kg/kg`。M1、M2 数值检查均通过。

证据：`experiments/EXP-002/metrics.json`

适用范围：1800 s、`dt=1 s`、`N=80`、线性插值、Robin 边界。

限制：B0 是均匀 Baseline，M2 是消融模型；该比较不单独决定最终主模型。

状态：SUPPORTED

## FIND-Q2-008 长时 ENV-A 数值稳定性与低含水率物性范围

问题：Q2

发现：Candidate A（`n=80`、`dt=0.25 s`、BE startup/BDF2、linear、harmonic）在 ENV-A last raw point 后常值延续下完成 `0–259200 s`。各阶段场值有限且含水率为正；最终阶段 Picard 次数为 `2/2/2/2`（min/median/p95/max），`C` 范围为 `0.0516273255–2.55 kg/kg`，`D` 最小值为 `2.6499175e-12 m²/s`。最终阶段单步质量残差最大 `2.3387e-11`，热残差最大 `1.7792e-10 J`，Robin 热/质边界残差最大分别为 `1.2097e-8 W/m²` 与 `1.6771e-13 kg/m²/s`。

证据：`experiments/EXP-Q2-016-LONG-ENV-A-last-raw/stage_259200s.json`、`metrics.json`、`diagnostics_1s_recovered.csv`。

限制：这是数值稳定性和实现诊断证据，不是对 72 h 物理真实性、Q2 官方终点或最终结果文件的批准。`C<0.15` 只被被动观察，在 `205913–205913.25 s` 首次形成 bracket，没有触发停止。

状态：SUPPORTED

## FIND-Q2-009 Post-14400 s 环境规则会改变 Q2 长时场

问题：Q2

发现：相同网格和时间步下，ENV-A（last raw point）与 ENV-B（最后40点均值）在 6/24/48/72 h 的最大温度差分别为 `0.169486/0.169750/0.169750/0.169750 °C`，最大含水率差分别为 `0.0014492/0.0007154/0.0003763/0.0002776 kg/kg`。尾段审计显示 ENV-A 在 14400 s 后连续保持最后原始点，而 tail40 mean 会产生约 `-0.16975 °C` 的输入改变；因此环境尾段不能根据“差异很小”被静默选择。

证据：`experiments/EXP-Q2-012-ENVIRONMENT/metrics.json`、`experiments/EXP-Q2-018-ENV-COMPARISON/metrics.json`。

限制：该结果支持人工决策，不证明哪一种尾段规则是题面唯一解释。OQ-Q2-ENV-001 保持 OPEN。

状态：SUPPORTED

## FIND-Q2-010 插值与界面平均的敏感性边界

问题：Q2

发现：linear 与纯 Python PCHIP 均逐点复现附件1原始 knots，但在 0–4 h 的 Candidate A 比较中最大差异为 `0.0089368847 °C` 与 `1.6431732e-5 kg/kg`，因此 PCHIP 不能被视为与 linear 数值等价。真实 Q2 0–3 h 中 arithmetic/harmonic face mean 最大差异仅为 `1.36852384e-6 K` 与 `4.94771902e-7 kg/kg`，独立变量系数 benchmark 仍通过守恒/阶数检查；在当前成本和证据下 arithmetic 是待人工批准的低成本推荐。

证据：`experiments/EXP-Q2-013-INTERPOLATION/metrics.json`、`experiments/EXP-Q2-015-INTERFACE-MEAN/metrics.json`。

限制：linear、arithmetic 仍是 provisional recommendation，不是已冻结的官方解释；OQ-Q2-ENV-002 与 OQ-Q2-FVM-001 保持 OPEN。

状态：SUPPORTED

## FIND-Q2-011 长时离散、重启和 Baseline 证据

问题：Q2

发现：长时 `dt=1/.5 s` 与 `n=20/40` 对 `n=80, dt=.25 s` recovered reference 的比较没有出现非有限场或误差随时间失控；该组 relative-to-finest 数字只作为长时 proxy，Q2 正式短时 observed order 仍引用固定空间/固定时间的 EXP-Q2-005/006。12 h checkpoint restart 到24 h 与连续运行的最终温度/含水率字段差均为 `0.0`。Q2-B0 固定初始物性控制运行成本约为 coupled run 的 `0.2077`，但 6 h 含水率差为 `0.392241 kg/kg`，不能替代耦合模型。

证据：`experiments/EXP-Q2-017-LONG-CONVERGENCE/metrics.json`、`experiments/EXP-Q2-019-LONG-RESTART/metrics.json`、`experiments/EXP-Q2-020-BASELINE/metrics.json`。

限制：长时 proxy 不是完整 `dt=1/.5/.25/.125` 或 `dr=.1/.05/.025` 的新正式阶数证明；终点/行数和精度门仍待人工冻结。

状态：SUPPORTED
