# Q1 Visualization Package

状态：`COMPLETE`

本文件登记 Q1 冻结结果的可视化交付。图表只读取 `experiments/Q1_FREEZE_RUN/run_1/internal_output_reference.pkl.gz`、全时域收敛证据和冻结配置，不重新运行 solver，不修改 `result1.xlsx`。所有图表均保留 PNG/SVG 两种格式，并由 `scripts/validate_q1_figures.py` 校验。

## Source and Traceability

- 冻结内部输出：`experiments/Q1_FREEZE_RUN/run_1/internal_output_reference.pkl.gz`
- 受保护源 SHA-256：`f13667b5fe8e4c1e1a7635b18ab4c7aaa9e3fef5111b893a9ce79b6deb3fad17`
- 图表清单：`figures/q1/FIGURE_MANIFEST.json`
- 图表验证：`figures/q1/FIGURE_VALIDATION.json`
- 生成脚本：`scripts/generate_q1_figures.py`
- 验证脚本：`scripts/validate_q1_figures.py`

## Figure Register

| Figure ID | Title | Purpose | Suggested paper placement | Source |
|---|---|---|---|---|
| FIG-Q1-01 | Temperature radial profiles | 展示若干时刻温度沿半径的剖面变化 | Q1 结果分析 | freeze internal output |
| FIG-Q1-02 | Moisture radial profiles | 展示若干时刻含水率沿半径的剖面变化 | Q1 结果分析 | freeze internal output |
| FIG-Q1-03 | Temperature time-radius heatmap | 展示温度随时间和半径的二维演化 | Q1 结果总览 | freeze internal output |
| FIG-Q1-04 | Moisture time-radius heatmap | 展示含水率随时间和半径的二维演化 | Q1 结果总览 | freeze internal output |
| FIG-Q1-05 | Temperature histories at selected radii | 对比中心、内部和表面的温度时间历史 | Q1 结果分析 | freeze internal output |
| FIG-Q1-06 | Moisture histories at selected radii | 对比中心、内部和表面的含水率时间历史 | Q1 结果分析 | freeze internal output |
| FIG-Q1-V01a | Spatial convergence | 展示三层聚簇空间配置的收敛证据 | 数值验证 | `EXP-Q1-FULL-SPATIAL/metrics.json` |
| FIG-Q1-V01b | Temporal convergence | 展示三层 BDF2 时间步长的收敛证据 | 数值验证 | `EXP-Q1-FULL-TEMPORAL/metrics.json` |
| FIG-Q1-V02 | Early surface moisture error decay | 展示初始层诊断中的早期表面误差衰减 | 数值诊断/局限性 | `EXP-Q1-SURFACE-DECAY/metrics.json` |

## Validation Contract

- 图表数量：9 个 Figure ID；每个 Figure ID 均有 PNG 与 SVG。
- 核心图表数组：7201 个内部时刻 × 339 个 solver 节点；不把内部节点误称为官方输出网格。
- 论文表追踪：温度 35/35、含水率 35/35；合计 70/70 个点与冻结结果一致。
- 图表随机数据追踪：20/20 个抽样点与冻结内部输出一致。
- PNG 资产：非空，尺寸满足验证脚本的可读性下限；已完成人工视觉 QA。

图表用于呈现计算结果和验证证据，不单独证明物理模型的现实校准、因果性或超出已登记假设范围的结论。
