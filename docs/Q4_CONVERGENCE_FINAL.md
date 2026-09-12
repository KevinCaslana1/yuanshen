# Q4 Numerical Convergence Finalization Audit

日期：2026-09-13

## 结论

Q4 数值收敛最终化：`HOLD`。Q4 历史冻结文件 `deliverables/final/result4.xlsx` 保持不变；没有生成 `deliverables/candidate_reaudit/result4.xlsx`，没有更新 Q4 manifest、Table6 或 Q4 论文图。

本轮使用独立、fresh-from-`t=0` 的 FVM/Backward Euler/Picard 参考实现。A/B/C/D 用于分离时间误差和空间误差，随后按照空间主导结论仅运行了最小必要的 `n=192, dt=2 s` 层级，并在该配置的事件跨越步内将 root bracket 细化到 `0.0625 s`。

## A/B/C/D 误差分解

| 配置 | 网格/时间步 | `t4` (s) | `t4` (h) | 控制点 |
|---|---:|---:|---:|---|
| A | `n=96, dt=4 s` | `191097.7336758627` | `53.082703798850744` | 中心 `r=0`, `xi=0` |
| B | `n=96, dt=2 s` | `191092.92436837355` | `53.08136788010376` | 中心 `r=0`, `xi=0` |
| C | `n=144, dt=4 s` | `190193.41146321915` | `52.83150318422754` | 中心 `r=0`, `xi=0` |
| D | `n=144, dt=2 s` | `190188.60538950787` | `52.830168163752184` | 中心 `r=0`, `xi=0` |

差分定义和结果：

- `Δ_time_n96 = B - A = -4.8093074891 s = -0.0013359187 h`
- `Δ_time_n144 = D - C = -4.8060737113 s = -0.0013350205 h`
- `Δ_space_dt4 = C - A = -904.3222126435 s = -0.2512006146 h`
- `Δ_space_dt2 = D - B = -904.3189788657 s = -0.2511997164 h`

空间效应约为时间效应的 `188.0358` 倍，主导误差判定为 `SPATIAL DOMINANT`。因此没有运行 `n=144, dt=1 s`，而是选择 `n=192, dt=2 s`。

## 最小必要 refinement

`n=192, dt=2 s` 从 `t=0` 独立运行，事件跨越的粗区间为 `[189902.0, 189904.0] s`；局部 root bracket 为 `[189903.25, 189903.3125] s`，宽度 `0.0625 s`。结果为：

- `t4 = 189903.26003601108 s = 52.75090556555863 h`
- `Cmax_before = 0.15000000513548917`
- `Cmax_after = 0.1499999731538512`
- 控制点仍为中心 `r=0`, `xi=0`
- 最大逐步质量残差 `2.078960040194412e-4`
- 最大 Robin 残差 `1.491384711335097e-6`
- 最大 Picard 次数 `5`

固定 `dt=2 s` 的三层空间趋势为 `n=96 → 144 → 192`，即 `B → D → E`。细层 `D → E` 原始差为 `285.3453534968 s = 0.0792625982 h`；观测空间阶约 `2.8448` 仅作为趋势诊断，未使用 Richardson 外推。

## Paper acceptance criterion

| 项目 | 估计值 |
|---|---:|
| 论文四位小时数值不确定度门 | `0.00005 h` |
| 细层空间原始误差估计 | `0.0792625982 h` |
| 时间误差原始估计 | `0.0013359187 h` |
| 事件根局部分辨率 | `0.0000173611 h` (`0.0625 s`) |
| 保守合成不确定度 | `0.0806158781 h` |

保守不确定度远大于门限，故 `criterion_pass = false`。root-location error 已足够小，不能解释数百秒的场离散差异；阻塞项是 PDE field discretization uncertainty。

## PCHIP / linear radius sensitivity

只在选定的 `n=192, dt=2 s` 层级补做一次半径插值对照：

- PCHIP：`52.75090556555863 h`
- linear：`52.75694235084274 h`
- linear − PCHIP：`+21.7324270228 s = +0.0060367853 h`

保留 PCHIP。线性插值只作敏感性对照，不替代 PCHIP，也未用于贴合外部截图。

## 外部值处理

外部 `51.0823 h` 仅作 `EXTERNAL_REFERENCE`，不是拟合目标。当前最佳独立值与其相差 `1.6686055656 h`，但由于独立序列尚未达到收敛门，最终分类为：`C. 尚未收敛，无法判断外部值对应的模型/参数/实现`。

## 受保护资产与状态

- 未修改 `A题/`、`data/raw/`、`src/q4/`、`src/q2/`、Q1/Q2/Q3/Q4 final workbook。
- 未重新审计已经通过的 Appendix 4、Kelvin、Attachment 2、moving-domain 方程、Robin、Word 表格或 Q4 图表项目。
- 历史 Q4 `53.0827 h` 继续保留为冻结数值 artifact；`52.7509 h` 只属于独立 audit，不提升为 final。
- 证据目录：`experiments/Q4_CONVERGENCE_FINAL/`。
- 机器可读主记录：`experiments/Q4_CONVERGENCE_FINAL/q4_error_decomposition.json`。

```text
Q4 NUMERICAL CONVERGENCE = HOLD
DO NOT CHANGE FINAL RESULT4
```
