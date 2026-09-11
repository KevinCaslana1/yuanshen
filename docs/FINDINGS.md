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

限制：聚类 base640/base1280 与均匀 N1280 的跨网格族差异不能直接当作误差估计；聚类候选尚未完成 0–1800 s 全网格验证和主方案冻结。

状态：SUPPORTED

## FIND-Q1-014 早期 BE 子步未显示改善

问题：Q1

发现：在 N640、正常步长 `0.25 s` 下，将 0–1 s 改为 BE 子步并重新启动 BDF2，与标准“第一步 BE、随后 BDF2”比较时，启动子步 `0.25/0.125/0.0625 s` 的标准/早期最大差异分别为 `9.3725e-4`、`9.9496e-4`、`1.5769e-3 kg/kg`；t=1 s 表面对同一高精度标准参考的早期子步值没有显示单调改善。

证据：`experiments/EXP-Q1-BDF2-STARTUP/metrics.json`。

适用范围：M1-NUM-T2、N640、0–10 s 对照窗口。

限制：不能据此证明其他启动策略在全时段都无效；当前只决定不把早期子步直接冻结为生产策略。

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
