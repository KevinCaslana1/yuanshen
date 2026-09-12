# Handoff

Q1 已 FROZEN/COMPLETE，Q1 早期表面误差深谷已确认为 `pointwise error zero-crossing / cancellation dip`。Q2 V3 生产与交付候选门禁已完成；Q3/Q4 未启动。

## Q2 当前状态

- 状态：`Q2 RESULT & DELIVERABLE GATE COMPLETE`；`WAITING FOR HUMAN Q2 FREEZE APPROVAL`。
- 唯一生产源：`experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv`，manifest 状态 `PRODUCTION_CANONICAL`，SHA 见 `experiments/Q2_FREEZE_RUN_V3/output_hashes.json`。
- Run1/Run2 均 fresh `t=0`，V3 配置 n=320/cluster3、early `.015625 s` through5 s、production `.25 s`、BE/BDF2、harmonic、ENV-B；raw、整数秒采样、diagnostics 全量 byte/hash identical。
- passive bracket `[206935.0,206935.25] s` 仅用于 `final_horizon=228536 s` 的安全尾段规则，不是 Q3 drying time。

## 交付物

- candidate workbook：`deliverables/candidate/result2.xlsx`，仅 candidate，未进入 `deliverables/final/`。
- workbook audit：`experiments/Q2_FREEZE_RUN_V3/candidate_validation.json`，100/100 分层 trace、Table3/4 60/60、无公式、四位小数。
- figures：`figures/q2/final/` 中 FIG-Q2-01…08 和 FIG-Q2-V01…V03，数据及 manifest 在 `figures/q2/data/` 与 `figures/q2/FIGURE_MANIFEST.json`。
- 结果/门禁：`experiments/Q2_FREEZE_RUN_V3/validation.json`、`figure_validation.json`、`lineage.json`、`determinism.json`。

## 需要保持的边界

- 不修改 `src/q2/*`、生产配置、环境逻辑、采样逻辑、官方 `A题/` 或 Q1 冻结资产。
- 不把 formal-output 证书扩写为 n=640 full-horizon proof；不把 `14400.25 s` internal probe 写成正式输出失败或物理异常。
- 不把 candidate 自动升级为 final；等待人工 Q2 freeze approval 后才可考虑 candidate→final 的隔离复制。
- 公共 Git 仅本地提交，不推送。

## 历史 provenance

- `Q2_FREEZE_RUN/`：原始 accuracy gate failed，非来源。
- `Q2_FREEZE_RUN_V2/`：n=640 full-horizon attempt aborted，非来源。
- `Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912/` 与 `Q2_FREEZE_RUN_V3_POSTPROCESS_FAILURE_20260912/`：V3 失败尝试/非数值后处理故障，非来源。
