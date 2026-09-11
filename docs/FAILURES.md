# Failures

## F-Q1-002 — EXP-003 comparison helper rejected valid different time histories

- **Status:** FIXED
- **Observed:** The first EXP-003 run stopped before writing evidence because the comparison helper required the two runs to have the same number of stored snapshots. Different time steps necessarily produce different history lengths.
- **Cause:** The helper only needs matching final times for the requested final-field sensitivity comparison, but it checked both history length and final time.
- **Fix:** Relaxed the check to require matching final times only. Re-ran the affected experiment from EXP-003 after the fix.
- **Impact:** No official source, deliverable workbook, or experiment evidence was overwritten; the failed attempt produced no evidence directory.
- **Reproducibility:** The failed command was `.\\.venv\\Scripts\\python.exe scripts\\run_q1_experiments.py EXP-003` at implementation commit `ff9a4a759cb6143aaef19c5bec9074449d78e44c`.

这里只记录未来值得知道、能够避免重复踩坑的失败，不记录普通语法错误或一次性调试输出。

## 失败索引

| ID | 实验 | 方法 | 现象 | 最终判断 | 重试条件 |
|---|---|---|---|---|---|
| F-Q1-001 | EXP-001 | 直接执行 `scripts/run_q1_smoke.py` | `ModuleNotFoundError: No module named 'src'` | 入口脚本缺少项目根目录路径注入，已修复；不是数值失败 | 修复后重新运行 EXP-001 |
| F-Q1-003 | EXP-Q1-FINAL-CONV | 完整输出网格四位小数稳定性 | N160→N320 与 dt1→dt0.25 仍有大量报告值变化 | 当前精度门阻塞；不是求解器崩溃，也不授权放宽门槛 | 人工决定数值整改方案后重跑完整门 |

## 失败记录模板

```markdown
## F-xxx 标题

对应实验：EXP-xxx
方法：
现象：
失败原因：
已尝试修复：
最终判断：
是否放弃：是/否
重新尝试条件：
```

## F-Q1-001 Q1 smoke 入口路径缺失

对应实验：EXP-001

方法：使用 `.venv` 直接执行 `scripts/run_q1_smoke.py`。

现象：Python 无法导入项目包 `src`。

失败原因：直接执行脚本时，解释器的模块搜索路径未自动包含项目根目录。

已尝试修复：在脚本启动处显式加入脚本父目录对应的项目根目录。

最终判断：这是启动入口缺陷，不是 Q1 方程、离散或求解器数值失败。

是否放弃：是，作为本次入口修复后的历史故障保留。

重新尝试条件：修复后重新运行 EXP-001，并确认后续正式实验只能在 smoke PASS 后启动。

## F-Q1-003 Q1 最终输出级数值精度门阻塞

对应实验：EXP-Q1-FINAL-CONV

方法：固定 M1、线性边界输入、Robin 边界和 Picard 收敛参数；空间依次测试 `N=80/160/320`（`dt=0.25 s`），时间依次测试 `dt=1/0.5/0.25 s`（固定 `N=320`）。每次比较完整 `1800×21` 交付网格和论文 `7×5` 追踪点，分别检查原始差异与 `ROUND_HALF_UP` 四位小数后的单元格稳定性。

现象：空间最细比较 N160→N320 的完整网格仍有温度 `1398/37800`、水分 `4468/37800` 个四位小数差异；时间最细比较 dt1→dt0.25 的完整网格仍有温度 `36498/37800`、水分 `6926/37800` 个差异。论文点也未全量稳定。

失败原因：在当前已测试内部网格和时间步长序列下，输出级四舍五入结果未达到“所有单元稳定”的交付门槛。该结果只说明测试配置未通过，不证明模型方程或求解器必然错误。

已尝试修复：已完成空间细化至 `N=320` 和时间细化至 `dt=0.25 s` 的门控比较；没有修改容差、交付契约或官方资产。

最终判断：Q1 最终数值准确性门 `BLOCKED`；不生成 candidate/final `result1.xlsx`，不执行 `Q1_FREEZE_RUN`，不启动 Q2。

是否放弃：否。

重新尝试条件：人工审查数值整改方案并明确允许的模型/离散调整后，重新登记并运行新的唯一实验编号；不得仅放宽四舍五入稳定性标准。
