# Q1 Final Freeze Audit

状态：`COMPLETE / HUMAN FREEZE APPROVED`
日期：2026-09-11
范围：仅 Q1；不修改 `A题/`，不启动 Q2/Q3/Q4。

## Human Freeze Decision

`Q1 HUMAN FREEZE APPROVAL = APPROVED`

批准对象为 Q1 M1 物理模型、生产数值配置、candidate 到 final 的字节复制、最终工作簿验证、清单和可视化交付。批准不扩大到 Q2/Q3/Q4，也不授权改变 Q1 模型、初值、Robin 参数或启动策略。

## Code and Evidence Baselines

- Q1 冻结运行代码基线：`a40ca421c33a2bd688c8f6e3b72816a03c49b2b0`
- 冻结前交付审计基线：`3068ff1eb86cc1657d856cc0796350fa6533ae91`
- 最终校验/图表流水线提交：`457bedcd8ebfcb4cf6e2da19c2d8a5aeaee39fbb`
- 冻结运行目录：`experiments/Q1_FREEZE_RUN/`
- 图表目录：`figures/q1/`

## Frozen Q1 Configuration

- 模型：M1，一维径向、轴对称、固定半径、常物性导热、非线性 `D(C)`、Robin 换热/传质边界。
- 空间：边界聚簇保守径向 FVM，`cluster_power=2`；base320 为请求网格，实际 `338` 个控制体、`339` 个节点；显式保留全部官方输出节点。
- 节点映射：`R * (1 - (1 - i/320)^2)` 与官方输出节点取并集。
- 节点间距：最小 `1.953124999995448e-07 m`，最大 `0.00012480468750000195 m`，最大/最小比约 `639.0000000014992`。
- 时间：`0..1800 s`，输出时刻为 `1..1800 s`；固定 `dt=0.25 s`；首步 Backward Euler，随后固定步长 BDF2。
- 非线性求解：Picard tolerance `1e-8`，最大迭代 `50`。
- 输出：`1800 × 21` 个数值单元；时间轴 `1..1800 s`；半径 `0..2 cm`、间隔 `0.1 cm`；最终显示四位小数。
- 单位：温度 `°C`，含水率 `kg/kg`；内部计算保持完整精度，最终工作簿按交付契约输出。

## Numerical Accuracy

全时域空间/时间证据均通过团队数值门：

- 最大估计温度离散不确定度：`1.4012174801763968e-06 °C`。
- 最大估计含水率离散不确定度：`2.7414224748183296e-05 kg/kg`。
- 阈值：温度和含水率均 `<5e-5`（各自输出单位）。
- `Q1_FREEZE_RUN` 两次从零运行的完整内部输出 SHA-256 完全一致：`f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17`。

少量 `ROUNDING_AMBIGUOUS` 只作为辅助诊断，未被用作自动否决；最终工作簿值来自冻结运行源并按既定四舍五入规则写出。

## Deliverable and Traceability

- Candidate：`deliverables/candidate/result1.xlsx`，SHA-256 `06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c`。
- Final：`deliverables/final/result1.xlsx`，SHA-256 `06b67b1f688d84a701ac4d2f4b0f47a1624069877df6724faf071a48af177b5c`。
- Candidate/final：字节级 SHA-256 完全一致。
- Final workbook：`scripts/validate_q1_final.py` PASS；形状为 `1801 × 22`，两张官方 Sheet、时间/距离轴、有限值、四位小数、无公式和官方模板哈希均通过。
- Paper trace：温度 `35/35`、含水率 `35/35`，合计 `70/70` 个论文点与冻结运行一致。
- Manifest：`deliverables/final/Q1_MANIFEST.json` PASS，记录生产配置、源资产哈希、结果哈希和验证报告。

## Visualization Traceability

- 图表清单：`figures/q1/FIGURE_MANIFEST.json`，共 9 个 Figure ID，每个均有 PNG/SVG。
- 图表验证：`figures/q1/FIGURE_VALIDATION.json`，状态 PASS。
- 图表源哈希受保护；核心图表随机数据点 `20/20` 通过。
- 图表与最终工作簿论文点合计 `70/70` 通过。
- 9 张图表已完成人工视觉 QA；图表仅用于结果展示和数值验证，不扩大论文主张。

## Official Source Integrity

- `A题/` 保持 OFFICIAL_SOURCE / IMMUTABLE_SOURCE。
- 官方输入和结果模板哈希由 `docs/DATA_CATALOG.md` 与验证脚本登记；`result1.xlsx` 官方模板哈希为 `23b261b295c1b787d000eebbca6521c37075107b6fcf78724f8d395ce1798ff4`。
- 最终结果由官方模板副本隔离生成；未直接写入、覆盖、删除或重命名 `A题/` 中资产。

## Remaining Risks and Boundary

- Q1 的 `A-Q1-001` 一维径向假设、`hm` 口径和物理简化仍是项目账本中的建模假设/决策，不应写成官方事实。
- 当前没有 Q1 交付阻塞；仓库为 Public，因此本轮只做本地提交，不推送 GitHub。
- Q2/Q3/Q4 均为 `NOT STARTED`；下一步必须等待 Q2 model design authorization。
