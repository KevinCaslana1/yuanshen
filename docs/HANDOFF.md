# Handoff

> 本文件保持很短，只服务于新会话、上下文压缩或其他 Agent 的快速接管。

## 当前状态

Q1 已 FROZEN/COMPLETE，Q1 signed-error 深谷已确认是 `pointwise error zero-crossing / cancellation dip`。Q2 formal-output accuracy gate 已完成：transition/early formal lattice、3–48 h targeted reference、passive/final screen 均通过；Q2 V3 freeze run 尚未授权，candidate/result2 继续 fail-closed。Q3/Q4 未启动。

## Q2 正式来源

- Formal source：`NONE`；`experiments/Q2_FREEZE_RUN/run_1/official_samples.csv` 仅为 `FAILED_PRODUCTION_ATTEMPT` provenance。
- Old Run1/Run2 fresh `t=0`，horizon `228635 s`；raw/sampled/diagnostics/checkpoint byte/hash identical，但 accuracy gate FAIL。
- 配置：Candidate A，实际98 cells，`dt=.25 s`，BE startup/BDF2，linear，harmonic，post-14400 constants `49.99525 °C/0.049988 kg/kg`。
- Passive observer bracket `[207034.5,207034.75] s` 仅用于安全尾段规则，不是 Q3 最终 drying time。

## 历史阻塞证据

`experiments/Q2_FREEZE_RUN/accuracy_confirmation.json` 为 `FAIL`：T/C L∞=`1.9082196854469657e-4/2.0357404664261836e-4`，T/C L2=`4.400124076121024e-6/3.0182278875418313e-5`，内部门为 `2.5e-5`。最大 T temporal 峰在 `14401 s,2.0 cm`，由冻结环境跳变定位；最大 C spatial 峰在 `1 s,2.0 cm`，由初始表面层分辨率定位。当前证据不证明 solver assembly bug，但证明候选不能交付。

## 当前证书

- `experiments/Q2_ACCURACY_REMEDIATION/accuracy_confirmation_v3.json` 是当前 formal-output 证书；formal transition T/C L∞=`1.55375452663975e-5/3.1402255240564614e-9`，early policy5 T/C L∞=`7.116765686987492e-6/1.0270424274150258e-5`。
- `14400.25 s,r=2.0 cm` 温度 internal peak=`2.2991211631051556e-4 °C`，在 integer outputs 未传播，分类为 `SUPPORTED_INTERNAL_TRANSITION_DIAGNOSTIC`。
- `experiments/EXP-Q2-ACC-LONG-TARGETED/`：3–48 h n640 局部 reference T/C L∞=`1.2509725024756335e-6/2.987415287369899e-6`；n640 没有推进到 full horizon，文档明确为 targeted certificate。

## 下一步约束

等待人工授权 `Q2_FREEZE_RUN_V3`；授权后必须使用新 attempt 目录，从 `t=0` 做双跑、determinism、lineage、official sampler、candidate workbook 和 figures 验证。不得续跑 `Q2_FREEZE_RUN_V2`，不得在授权前生成 `deliverables/candidate/result2.xlsx`、Q2 figures 或启动 Q3/Q4。保持 `A题/` 和 Q1 final/figures 不变。

## 关键文件

`docs/Q2_ACCURACY_REMEDIATION.md`、`docs/Q2_PRODUCTION_FREEZE.md`、`docs/Q2_RESULT_AUDIT.md`、`docs/STATE.md`、`docs/VALIDATION.md`、`experiments/Q2_ACCURACY_REMEDIATION/accuracy_confirmation_v3.json`、`experiments/EXP-Q2-ACC-T-FORMAL/`、`experiments/EXP-Q2-ACC-C-FORMAL/`、`experiments/EXP-Q2-ACC-LONG-TARGETED/`、`experiments/Q2_FREEZE_RUN/accuracy_confirmation.json`、`experiments/Q2_FREEZE_RUN_V2/ABORTED_ATTEMPT.json`。
