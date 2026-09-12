# Handoff

Q1 已 FROZEN/COMPLETE，Q1 早期表面误差深谷已确认为 `pointwise error zero-crossing / cancellation dip`。Q2 V3 已完成 production freeze；Q3/Q4 未启动。

## Q2 当前状态

- 状态：`Q2 = FROZEN`；V3 production freeze approval `APPROVED`。
- 唯一生产源：`experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv`，manifest 状态 `PRODUCTION_CANONICAL`，SHA 见 `experiments/Q2_FREEZE_RUN_V3/output_hashes.json`。
- Run1/Run2 均 fresh `t=0`，V3 配置 n=320/cluster3、early `.015625 s` through5 s、production `.25 s`、BE/BDF2、harmonic、ENV-B；raw、整数秒采样、diagnostics 全量 byte/hash identical。
- passive bracket `[206935.0,206935.25] s` 仅用于 `final_horizon=228536 s` 的安全尾段规则，不是 Q3 drying time。

## 交付物

- final workbook：`deliverables/final/result2.xlsx`；由 `deliverables/candidate/result2.xlsx` 按字节原样复制，SHA-256 与文件大小完全一致；冻结记录：`experiments/Q2_FINAL_FREEZE/freeze_record.json`。
- workbook audit：`experiments/Q2_FREEZE_RUN_V3/candidate_validation.json`，100/100 分层 trace、Table3/4 60/60、无公式、四位小数。
- figures：`deliverables/final/figures/q2/` 中 FIG-Q2-01…08 和 FIG-Q2-V01…V03；11 组 PNG/SVG、PNG ≥300 dpi、trace 30/30；交付清单：`deliverables/final/Q2_MANIFEST.json`。
- 结果/门禁：`experiments/Q2_FREEZE_RUN_V3/validation.json`、`figure_validation.json`、`lineage.json`、`determinism.json`。

## 需要保持的边界

- 不修改 `src/q2/*`、生产配置、环境逻辑、采样逻辑、官方 `A题/` 或 Q1 冻结资产。
- 不把 formal-output 证书扩写为 n=640 full-horizon proof；不把 `14400.25 s` internal probe 写成正式输出失败或物理异常。
- 不重新计算 Q2、不重新绘图、不改写已验证 workbook/figure 内容；Q2 final 只接受已验证 candidate 的 COPY ONLY 结果。
- 公共 Git 仅本地提交，不推送。

## 历史 provenance

- `Q2_FREEZE_RUN/`：原始 accuracy gate failed，非来源。
- `Q2_FREEZE_RUN_V2/`：n=640 full-horizon attempt aborted，非来源。
- `Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912/` 与 `Q2_FREEZE_RUN_V3_POSTPROCESS_FAILURE_20260912/`：V3 失败尝试/非数值后处理故障，非来源。
