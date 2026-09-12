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
| FIND-Q2-017 | 批准的 Q2 冻结生产双跑可重复但精度门未通过 | Q2 | Q2_FREEZE_RUN、accuracy_confirmation | SUPPORTED（候选阻塞） |
| FIND-Q2-018 | 14400 s 环境跳变和 1 s 初始表面层分别主导最大误差峰 | Q2 | Q2_FREEZE_RUN/environment.json、accuracy_diagnosis | SUPPORTED（需新整改决定） |
| FIND-Q2-019 | Q2 初始表面 Robin 不相容性已独立复算，限定为数值初始层发现 | Q2 | EXP-Q2-ACC-C-INITIAL | SUPPORTED（不改变初值或物理参数） |
| FIND-Q2-020 | 环境跳变处 BE restart 降低了 common integer-time 局部 raw bound，但不自动证明全时域通过 | Q2 | EXP-Q2-ACC-T-TRANSITION | SUPPORTED（局部数值证据） |
| FIND-Q2-021 | Q2 时间/空间误差已分离；细化后 raw L∞ 均下降，未使用乐观 Richardson | Q2 | EXP-Q2-ACC-SPATIAL*、EXP-Q2-ACC-TEMPORAL* | SUPPORTED（raw/conservative bound） |
| FIND-Q2-022 | n=320、cluster_power=3 在 0–2 s 表面含水率相对 n=640、cluster_power=2 的差低于门槛 | Q2 | EXP-Q2-ACC-SPATIAL-CLUSTER3 | SUPPORTED（短时候选证据） |
| FIND-Q2-023 | V2 候选在 formal integer-time transition points 低于门槛；`14400.25 s` 局部探针温度差为 `2.2991e-4 °C` 且未传播到整数秒 | Q2 | EXP-Q2-V2-REGRESSION、EXP-Q2-ACC-T-FORMAL | SUPPORTED（internal diagnostic only） |
| FIND-Q2-024 | n=640 V2 full-horizon 尝试因当前逐步求解成本过高而中止，不能作为完成或精度证据 | Q2 | Q2_FREEZE_RUN_V2/ABORTED_ATTEMPT.json | SUPPORTED（性能阻塞） |
| FIND-Q2-025 | Formal-output scope 下 transition integer lattice、early official lattice 和 selected long points 均通过 2.5e-5 raw/conservative gate | Q2 | accuracy_confirmation_v3.json、EXP-Q2-ACC-T-FORMAL、EXP-Q2-ACC-C-FORMAL、EXP-Q2-ACC-LONG-TARGETED | SUPPORTED（localized certification；非 full-horizon n640） |
| FIND-Q2-026 | 早期 fine startup 从 2 s 延长到 5 s 后，t=3 s/r=2 cm 的水分超限由 `4.723355270153107e-5` 降至全局 `1.0270424274150258e-5 kg/kg` | Q2 | EXP-Q2-ACC-C-FORMAL/metrics.json | SUPPORTED（step-policy transient evidence） |
| FIND-Q2-027 | n=320/cluster3 与局部 n=640 参考的 3–48 h 定点比较通过，passive/final 的 n=160 screen 也低于门槛；未执行 n=640 full horizon | Q2 | EXP-Q2-ACC-LONG-TARGETED/metrics.json | SUPPORTED（targeted long-horizon only） |
| FIND-Q2-028 | V3 Run1/Run2 均从 t=0 完成，raw/sampled/diagnostics/checkpoint 全量 byte/hash identical，228536 步 Picard non-converged=0 | Q2 | Q2_FREEZE_RUN_V3/metrics.json、determinism.json | SUPPORTED |
| FIND-Q2-029 | V3 Run1 是唯一 PRODUCTION_CANONICAL 来源；candidate workbook 与 11 组图表完成独立结构、精度、溯源和分辨率验证，并按 COPY ONLY 进入 final | Q2 | Q2_CANONICAL_DATA_MANIFEST.json、Q2_FREEZE_RUN_V3/candidate_validation.json、Q2_FINAL_FREEZE/freeze_record.json、figures/q2/ | SUPPORTED |

## FIND-Q2-019 Q2 初始表面 Robin 不相容性已独立复算

问题：Q2

发现：在不修改官方初值、`hm`、`D` 或表面环境的情况下，Q2 自身重算得到 `C0=2.55 kg/kg`、`C_inf(0)=0.01963 kg/kg`、`hm=8e-7 m/s`、`D(C0,T0)=5.641680373025664e-9 m²/s`。均匀初始离散扩散通量为 `0`，Robin 通量为 `2.0242959999999997e-6 kg/(m²·s)`，residual 为 `-2.0242959999999997e-6 kg/(m²·s)`。

证据：`experiments/EXP-Q2-ACC-C-INITIAL/metrics.json`

限制：这只是 Q2 numerical initial-layer finding，不是“真实药材一定形成物理边界层”的结论。

状态：SUPPORTED

## FIND-Q34-001 Q3/Q4 独立核验结果

问题：Q3/Q4

发现：对冻结 Q3 输入 raw 的独立全时域扫描复现了 `206935 s` 仍不满足、`206936 s` 首次严格满足的阈值关系；独立 `n=20/40` 局部细化的 Q3 事件小时值均为 `57.4820 h`。对 Q4，独立 n=96、dt=4 s 从 `t=0` 得 `53.082703798850744 h`，与冻结 production 值一致到亚毫秒；但更细 n=144、dt=2 s 得 `52.830168163752184 h`，四位小时值不稳定。

因此 Q3 独立核验为 PASS；Q4 只能记录为 `INDEPENDENT VERIFICATION HOLD`，现有 `deliverables/final/result4.xlsx` 保持不变，新精化结果不提升为 final，也不作为截图拟合目标。Q4 独立恒半径回归、方程项审计、Table6 外域空值和表面列审计通过，但不足以覆盖事件时刻未收敛这一阻断项。

证据：`experiments/Q34_INDEPENDENT_AUDIT/audit.json`、`Q4_CONVERGENCE.csv`、`Q4_MOVING_DOMAIN_EQUATION_AUDIT.md`。

状态：SUPPORTED（Q4 收敛阻断为事实；Q4 论文使用仍需人工决定）

## FIND-Q3-001 Q3 固定半径阈值夹逼与局部细化

问题：Q3

发现：扫描冻结 Q2 V3 Run1 的 1 s、21 半径 raw lattice 得到 `Cmax(206935 s)=0.1500000658293865`，仍未满足 `C<0.15 kg/kg`；`Cmax(206936 s)=0.14999977460230157`，已满足。以 `t=206935 s` 状态做非 Excel 行插值的局部 BE/Picard 子步计算，在 `1/1024 s` 子步下首次严格低于阈值的 candidate endpoint 为 `t3=206935.2265625 s=57.4820073785 h`；端点全 21 个官方半径节点均低于阈值，critical node 由扫描得到为 `r=0.0 cm`。

证据：`experiments/Q3_PRODUCTION/q3_summary.json`、`q3_result3_matrix_full_precision.csv`、`validation.json`。

限制：Q2 没有保存 `206935 s` 的 n=320 restart state，故 endpoint 局部细化明确标记为 reconstructed official 0.1 cm lattice 的 candidate refinement；不得把它描述为 Q2 full-field restart 的严格复算。

状态：SUPPORTED（Q3 candidate scope）

## FIND-Q4-001 Q4 收缩半径候选的阈值与域映射

问题：Q4

发现：使用附录4物性、附件2单调 PCHIP 半径和材料坐标 `ξ=r/R(t)` 的 BE/Picard candidate 在 `[191096,191100] s` 发生阈值夹逼；局部细化得到 `t4=191097.7336093787 s=53.0827037804 h`，`R(t4)=1.2 cm`，`Cmax_before=0.15000087683231333`，`Cmax_after=0.14999885377291058`，critical material point 为 `ξ=0`（物理 `r=0 cm`）。附件2所有节点 PCHIP 回代误差为 `0`，固定物理位置超过当前半径的输出单元无伪值。

证据：`experiments/Q4_PRODUCTION/q4_summary.json`、`q4_result4_matrix_full_precision.csv`、`validation.json`、`deliverables/candidate/paper/figures/fig_5_15_q4_radius_pchip.*`。

限制：Q4 是 candidate model implementation，不是人工冻结结论；质量守恒诊断的最大归一化逐步残差为 `3.4553928505477293e-4`，Robin 独立离散通量差最大为 `4.5474756348265686e-7`，应随 final freeze 审查一并评估。Q3/Q4 之间的时间差只作候选比较，不写成模型优越性。

状态：SUPPORTED（Q4 candidate scope）

## FIND-Q4-002 Q4 时空误差分解仍未达到论文不确定度门

问题：Q4

发现：独立 fresh-from-`t=0` A/B/C/D 运行显示，固定 `n=96` 或 `n=144` 时把 `dt` 从 `4 s` 减到 `2 s` 只改变事件约 `4.8 s`（`0.00134 h`）；固定 `dt=2 s` 时把 `n` 从 `96` 增至 `144` 改变事件约 `904.3 s`，增至 `192` 后仍改变 `285.3 s`（`0.07926 h`）。因此当前主导误差为 `SPATIAL DOMINANT`。

最小必要 `n=192,dt=2 s` 的局部 root bracket 宽度为 `0.0625 s`，事件为 `52.7509055656 h`，控制点仍为中心 `r=0/xi=0`。PCHIP 与 linear 半径对照差为 `21.7324 s`；PCHIP 保留。

限制：细层空间原始误差、时间误差和 root 分辨率合成的保守不确定度约 `0.0806158781 h`，超过人工规定的 `0.00005 h` 论文门；观测空间阶 `2.8448` 只作趋势诊断，未进行 Richardson 外推。因此不得生成 Q4 corrected candidate，不得用 `52.7509 h` 替换冻结 `result4.xlsx`，也不能据此判断其是否接近外部 `51.0823 h`。

证据：`experiments/Q4_CONVERGENCE_FINAL/q4_error_decomposition.json`、`new_runs_B_C.json`、`next_refinement_n192_dt2.json`、`interpolation_sensitivity_n192_dt2.json`。

状态：SUPPORTED（Q4 convergence blocker）

## FIND-Q2-028 Q2 V3 生产双跑在正式输出范围内完成并确定性一致

问题：Q2

发现：在人工批准的 V3 冻结配置下，Run1 与 Run2 均从官方 t=0 初值独立启动；两次得到相同 passive bracket `[206935.0,206935.25] s` 和 `final_horizon=228536 s`。raw internal source、整数秒 official sampled source、1 s diagnostics 和 final checkpoint 均 byte/hash identical。Run1 的 228536 个时间步没有 non-converged step，Picard 迭代次数为 2–3。

限制：该发现证明本次生产执行的可复现性与诊断完整性，不把 formal-output certificate 扩写成 n=640 full-horizon 收敛证明；passive bracket 不是 Q3 drying time。

证据：`experiments/Q2_FREEZE_RUN_V3/metrics.json`、`determinism.json`、`output_hashes.json`、`lineage.json`

状态：SUPPORTED

## FIND-Q2-029 V3 Run1 是唯一 Q2 生产结果来源，候选交付通过独立溯源检查

问题：Q2

发现：canonical manifest 将 `experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv` 标记为唯一 `PRODUCTION_CANONICAL` 来源，Run2 仅为 `DETERMINISM_REFERENCE`。从 Run1 生成的 `deliverables/candidate/result2.xlsx` 两张表均为 228537 行×22 列（含表头），无公式、四位小数；分层 trace 为 100/100，Table 3/4 trace 为 60/60。Q2 图表包包含 11 组 PNG/SVG，PNG 分辨率不低于 300 dpi，30/30 trace 通过。

限制：final freeze 只证明交付文件与已验证 candidate 的字节一致，不扩展 formal accuracy certificate 的 declared scope；图表和工作簿均不得改写生产源。

证据：`experiments/Q2_CANONICAL_DATA_MANIFEST.json`、`experiments/Q2_FREEZE_RUN_V3/candidate_validation.json`、`experiments/Q2_FREEZE_RUN_V3/figure_validation.json`、`experiments/Q2_FINAL_FREEZE/freeze_record.json`、`figures/q2/FIGURE_MANIFEST.json`

状态：SUPPORTED

## FIND-Q2-020 环境跳变处 BE restart 改善 common-time 局部误差

问题：Q2

发现：在相同冻结 ENV-B、物理参数和 harmonic FVM 下，跨 `14400 s` 的 event-aligned BE restart 相比当前跨跳变 BDF2，在 n=80 局部细化的 common integer-time raw differences 中显著降低温度与水分误差；最细相邻 raw bound 为 T `8.143186960296589e-7 °C`、C `1.5011414333798712e-10 kg/kg`。这些数值是 fine/coarse differences，不是 Richardson uncertainty。

证据：`experiments/EXP-Q2-ACC-T-TRANSITION/metrics.json`

限制：显式探针 `14400.25 s` 不属于 common integer-time comparison；新 n=320 candidate regression 仍在该探针出现超门温度差，因此不能宣布完整 V2 通过。

状态：SUPPORTED

## FIND-Q2-021 Q2 时间和空间误差已分离

问题：Q2

发现：固定 `dt=.015625 s` 的 n320→n640 空间比较中，含水率 L∞ 从 `5.1707227172848036e-5` 降至进一步 n640 comparison 的 `1.297979618852807e-5 kg/kg`；固定 n640 的 dt=.015625→.0078125 时间比较中含水率 L∞ 为 `2.652957554083457e-6 kg/kg`，温度为 `2.100205165334046e-8 °C`。误差随独立维度细化下降，表格仅使用 raw difference/conservative bound。

证据：`experiments/EXP-Q2-ACC-SPATIAL/metrics.json`、`EXP-Q2-ACC-SPATIAL-FURTHER/metrics.json`、`EXP-Q2-ACC-TEMPORAL-FURTHER/metrics.json`

限制：这些是短时隔离证据，不替代 full-horizon accuracy confirmation。

状态：SUPPORTED

## FIND-Q2-022 n320/cluster_power=3 是早期表面空间候选

问题：Q2

发现：固定 `dt=.015625 s`、0–2 s、冻结物理和 harmonic face mean，n=320/cluster_power=3 相对于已完成 n=640/cluster_power=2 参考的温度/含水率 L∞ 分别为 `1.0052019661088707e-8 °C` 和 `2.5626144490864533e-6 kg/kg`，均低于 `2.5e-5` 局部门槛。

证据：`experiments/EXP-Q2-ACC-SPATIAL-CLUSTER3/metrics.json`

限制：这是短时 spatial candidate evidence，不证明长时误差、transition local probe 或 full-horizon 门通过。

状态：SUPPORTED

## FIND-Q2-023 V2 候选的 formal 时间点与 local first-post-step 分离

问题：Q2

发现：n=320/cluster_power=3、candidate dt=.25 s、early dt=.015625 s through 2 s、event-aligned BE restart 的 14500 s regression 中，formal integer-time `14390..14500 s` 的 T/C 最大 raw differences 为 `1.55375452663975e-5 °C` 和 `3.1402255240564614e-9 kg/kg`；显式 `14400.25 s,r=2.0 cm` local probe 的温度 raw difference 为 `2.2991211631051556e-4 °C`，其后在 `14400.50/14400.75/14401 s` 保持有界并未污染 formal lattice。

证据：`experiments/EXP-Q2-V2-REGRESSION/metrics.json`

状态：SUPPORTED；local probe is an internal diagnostic, not a delivery-point failure

## FIND-Q2-025 Q2 formal-output accuracy gate 在声明范围内完成

问题：Q2

发现：按 `D-Q2-ACCURACY-SCOPE`，transition 整数秒 `14395..14500 s` 六个重点半径的 T/C L∞ 为 `1.55375452663975e-5 °C` / `3.1402255240564614e-9 kg/kg`；早期正式时刻 `1,2,3,4,5,10,20,30,60,100,300,600,1800 s`、全部21个官方半径的 T/C L∞ 为 `7.116765686987492e-6 °C` / `1.0270424274150258e-5 kg/kg`。定点长时 3–48 h 的局部 n=640 参考 T/C L∞ 为 `1.2509725024756335e-6 °C` / `2.987415287369899e-6 kg/kg`，passive 邻域和最终点的独立 n=160 screen 低于门槛。

限制：该证书只覆盖声明的正式点集合，不是 n=640 全时域收敛证明，也不建立 `result2` production source；证据使用 raw fine/coarse difference，不使用 Richardson 外推。

证据：`experiments/Q2_ACCURACY_REMEDIATION/accuracy_confirmation_v3.json`、`experiments/EXP-Q2-ACC-T-FORMAL/`、`experiments/EXP-Q2-ACC-C-FORMAL/`、`experiments/EXP-Q2-ACC-LONG-TARGETED/`

状态：SUPPORTED

## FIND-Q2-026 早期 t=3 s 超限随 fine startup window 延长而消失

问题：Q2

发现：同一 n=320/cluster3 候选与同策略 n=640/cluster2 reference 的早期 formal 比较中，fine startup 只到 `2 s` 时，最大水分差为 `4.723355270153107e-5 kg/kg`，发生在 `t=3 s,r=2.0 cm`；把相同 fine startup window 延长到 `5 s` 后，最大水分差变为 `1.0270424274150258e-5 kg/kg`，位置为 `t=10 s,r=2.0 cm`，正式门通过。

解释：数据支持步长切换/多步启动策略引起的局部瞬态，而不是 20–40 s 的物理输入跳变或算法突然提高两个数量级。该解释不改变官方初值、环境和物理参数。

证据：`experiments/EXP-Q2-ACC-C-FORMAL/metrics.json`、`comparison.csv`

状态：SUPPORTED

## FIND-Q2-027 定点长时证书未显示晚期误差放大

问题：Q2

发现：新 n=320/cluster3 candidate 从 `t=0` 连续推进至 `228635 s`；3–48 h 六个正式时刻用连续 n=640/cluster2 局部 reference 比较，T/C L∞ 为 `1.2509725024756335e-6 °C` / `2.987415287369899e-6 kg/kg`。被动事件整数邻域 `207033..207036 s` 和最终点使用连续 n=160/cluster2 screen，水分最大差分别不超过 `2.008097424559263e-5` 和 `1.892403267497733e-5 kg/kg`。所有相关运行有限且 Picard/质量/热量诊断有记录。

限制：n=640 仅推进到48 h，因此不能写成 n=640 full-horizon convergence completed；历史 0–72 h 证据仅作为稳定性上下文。

证据：`experiments/EXP-Q2-ACC-LONG-TARGETED/metrics.json`

状态：SUPPORTED

## FIND-Q2-024 n640 V2 full-horizon 尝试因性能中止

问题：Q2

发现：n=640/cluster_power=2 的 V2 fresh Run1 在未完成 full horizon 前、约推进到 `888 s` simulated time 时被安全停止；没有写出完整 metrics、validation、Run2 或 workbook。部分 raw/diagnostic 文件保留作 provenance，不能恢复或消费。

证据：`experiments/Q2_FREEZE_RUN_V2/ABORTED_ATTEMPT.json`、`experiments/Q2_FREEZE_RUN_V2/notes.md`

限制：这是 execution-performance finding，不是物理或 accuracy PASS/FAIL 结论。

状态：SUPPORTED

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

## FIND-Q2-017 Q2 冻结生产双跑具有确定性，但精度门未通过

问题：Q2

发现：按批准的 Q2 production freeze 配置，Run1/Run2 均从 `t=0` 新鲜推进到 `228635 s`；raw、sampled、diagnostics 和 checkpoint 的 SHA-256 均相同。生产诊断中 Picard 次数为 `min/median/p95/max=2/2/3/3`，没有非收敛步；温度、水分、物性和中心对称检查为有限且有效。

证据：`experiments/Q2_FREEZE_RUN/metrics.json`、`determinism.json`、`output_hashes.json`。

限制：确定性只说明实现可重复，不等于离散精度门通过，也不等于官方结果接受。

状态：SUPPORTED

## FIND-Q2-018 冻结环境跳变和初始层分别主导两个最大误差峰

问题：Q2

发现：Attachment 1 在 `14400 s` 的值为 `(50.165 °C,0.04986 kg/kg)`，冻结 post-attachment 常值为 `(49.99525 °C,0.049988 kg/kg)`，存在 `(-0.16975 °C,+0.000128 kg/kg)` 的输入跳变。生产与 `dt=.125 s` 比较的最大温度误差为 `1.9082196854469657e-4 °C`，位于 `14401 s,r=2.0 cm`；生产与 `n=160` 比较的最大水分误差为 `2.0357404664261836e-4 kg/kg`，位于 `1 s,r=2.0 cm`。

证据：`experiments/Q2_FREEZE_RUN/environment.json`、`accuracy_diagnosis.json`、三份 `accuracy_confirmation/*_by_time.csv`。

限制：该证据支持“当前冻结候选未通过内部精度门”，不单独证明 solver assembly bug；post-14400 连续性、初始层分辨率和 accuracy gate 若要改变，必须重新人工决策。

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
