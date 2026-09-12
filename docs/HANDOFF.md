# Handoff

> 本文件保持很短，只服务于新会话、上下文压缩或其他 Agent 的快速接管。

## 当前状态

Q1 已 FROZEN/COMPLETE，Q1 signed-error 深谷已确认是 `pointwise error zero-crossing / cancellation dip`。Q2 原 production accuracy gate 失败；人工授权的数值整改已完成局部诊断和 14500 s regression，但 V2 full-horizon 未确认，Q2 candidate/result2 继续 fail-closed 阻止。Q3/Q4 未启动。

## Q2 正式来源

- Formal source：`NONE`；`experiments/Q2_FREEZE_RUN/run_1/official_samples.csv` 仅为 `FAILED_PRODUCTION_ATTEMPT` provenance。
- Old Run1/Run2 fresh `t=0`，horizon `228635 s`；raw/sampled/diagnostics/checkpoint byte/hash identical，但 accuracy gate FAIL。
- 配置：Candidate A，实际98 cells，`dt=.25 s`，BE startup/BDF2，linear，harmonic，post-14400 constants `49.99525 °C/0.049988 kg/kg`。
- Passive observer bracket `[207034.5,207034.75] s` 仅用于安全尾段规则，不是 Q3 最终 drying time。

## 阻塞证据

`experiments/Q2_FREEZE_RUN/accuracy_confirmation.json` 为 `FAIL`：T/C L∞=`1.9082196854469657e-4/2.0357404664261836e-4`，T/C L2=`4.400124076121024e-6/3.0182278875418313e-5`，内部门为 `2.5e-5`。最大 T temporal 峰在 `14401 s,2.0 cm`，由冻结环境跳变定位；最大 C spatial 峰在 `1 s,2.0 cm`，由初始表面层分辨率定位。当前证据不证明 solver assembly bug，但证明候选不能交付。

## 下一步约束

等待人工复核 `docs/Q2_ACCURACY_REMEDIATION.md`。n320/cluster3 candidate 的 formal integer transition points 低于门槛，但 `14400.25 s,r=2.0 cm` local temperature probe=`2.2991211631051556e-4 °C`；n640 V2 full attempt在约888 s因性能中止。若继续，必须使用新 attempt 目录并先解决/接受 local probe与运行成本；不得续跑 `Q2_FREEZE_RUN_V2`，不得生成 `deliverables/candidate/result2.xlsx`、Q2 figures 或启动 Q3/Q4。保持 `A题/` 和 Q1 final/figures 不变。

## 关键文件

`docs/Q2_ACCURACY_REMEDIATION.md`、`docs/Q2_PRODUCTION_FREEZE.md`、`docs/Q2_RESULT_AUDIT.md`、`docs/STATE.md`、`docs/VALIDATION.md`、`experiments/EXP-Q2-V2-REGRESSION/metrics.json`、`experiments/Q2_FREEZE_RUN/accuracy_confirmation.json`、`experiments/Q2_FREEZE_RUN_V2/ABORTED_ATTEMPT.json`。
