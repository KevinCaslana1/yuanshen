# Handoff

Q1 已 FROZEN/COMPLETE，Q1 早期表面误差深谷已确认为 `pointwise error zero-crossing / cancellation dip`。Q2 V3 已完成 production freeze。Q3/Q4 已获联合人工批准并完成 final freeze；未 push。

## Q2 当前状态

- 状态：`Q2 = FROZEN`；V3 production freeze approval `APPROVED`。
- 唯一生产源：`experiments/Q2_FREEZE_RUN_V3/run_1/official_samples.csv`，manifest 状态 `PRODUCTION_CANONICAL`，SHA 见 `experiments/Q2_FREEZE_RUN_V3/output_hashes.json`。
- Run1/Run2 均 fresh `t=0`，V3 配置 n=320/cluster3、early `.015625 s` through5 s、production `.25 s`、BE/BDF2、harmonic、ENV-B；raw、整数秒采样、diagnostics 全量 byte/hash identical。
- passive bracket `[206935.0,206935.25] s` 仅用于 `final_horizon=228536 s` 的安全尾段规则，不是 Q3 drying time。

## 交付物

- final workbook：`deliverables/final/result2.xlsx`；由 `deliverables/candidate/result2.xlsx` 按字节原样复制，SHA-256 与文件大小完全一致；冻结记录：`experiments/Q2_FINAL_FREEZE/freeze_record.json`。
- workbook audit：`experiments/Q2_FREEZE_RUN_V3/candidate_validation.json`，100/100 分层 trace、Table3/4 60/60、无公式、四位小数。
- figures：`deliverables/final/figures/q2/` 中 FIG-Q2-01…08 和 FIG-Q2-V01…V03；11 组 PNG/SVG、PNG ≥300 dpi、trace 30/30；交付清单：`deliverables/final/Q2_MANIFEST.json`。
- 中文 publication figures：`deliverables/final/paper/figures/q2/`；只读取既有 `figures/q2/data/`，11/11 PNG、11/11 SVG、11/11 PNG `300.101 DPI`、数据 trace `11/11`、中文文本检查 `11/11`；manifest/验证：`deliverables/final/paper/figures/q2/Q2_CHINESE_FIGURE_MANIFEST.json`、`experiments/Q2_CHINESE_FIGURE_LOCALIZATION/validation.json`。该目录与原 Q2 冻结图目录分离。
- 结果/门禁：`experiments/Q2_FREEZE_RUN_V3/validation.json`、`figure_validation.json`、`lineage.json`、`determinism.json`。

## 需要保持的边界

- 不修改 `src/q2/*`、生产配置、环境逻辑、采样逻辑、官方 `A题/` 或 Q1 冻结资产。
- 不把 formal-output 证书扩写为 n=640 full-horizon proof；不把 `14400.25 s` internal probe 写成正式输出失败或物理异常。
- 不重新计算 Q2、不改写已验证 workbook/原冻结 figure 内容；中文 publication version 仅允许从既有 Q2 图源数据后处理生成，不能改变数值数组。Q2 final workbook 仍只接受已验证 candidate 的 COPY ONLY 结果。
- 公共 Git 仅本地提交，不推送。

## 历史 provenance

- `Q2_FREEZE_RUN/`：原始 accuracy gate failed，非来源。
- `Q2_FREEZE_RUN_V2/`：n=640 full-horizon attempt aborted，非来源。
- `Q2_FREEZE_RUN_V3_FAILED_HORIZON_20260912/` 与 `Q2_FREEZE_RUN_V3_POSTPROCESS_FAILURE_20260912/`：V3 失败尝试/非数值后处理故障，非来源。

## Q3 最终状态

- 状态：`Q3 = FROZEN / COMPLETE`。
- 输入边界：只读 `deliverables/final/result2.xlsx` 与 `experiments/Q2_FREEZE_RUN_V3/run_1/official_samples_raw.csv`；Q2 final SHA=`84fb32457193e158debdf569d34f5f41b97e78496b30dd9b2e134385439e10da`。
- 结果：粗夹逼 `[206935,206936] s`；`t=206935` 的 `Cmax=0.1500000658293865`，`t=206936` 的 `Cmax=0.14999977460230157`；局部 BE/Picard 首个严格低于端点 `t3=206935.2265625 s=57.4820073785 h`，全 21 节点满足阈值，critical `r=0.0 cm`。
- 交付：`deliverables/final/result3.xlsx`、`deliverables/final/paper/tables/table5_q3.*`、`deliverables/final/paper/figures/q3/`、`deliverables/final/Q3_MANIFEST.json`、`docs/Q3_FINAL_FREEZE_AUDIT.md`。

## Q4 最终状态

- 状态：`Q4 = FROZEN / COMPLETE`。
- 方法：Appendix 4 properties；Attachment 2 `PchipInterpolator`-compatible monotone cubic；`ξ=r/R(t)` dynamic FVM/BE/Picard；Attachment 2 tail after `259200 s` holds at `R_last=1.198 cm`。
- 结果：粗夹逼 `[191096,191100] s`；`t4=191097.7336093787 s=53.0827037804 h`，`R(t4)=1.2 cm`，`Cmax_before=0.15000087683231333`，`Cmax_after=0.14999885377291058`，critical `ξ=0`/`r=0 cm`。
- 交付：`deliverables/final/result4.xlsx`、`deliverables/final/paper/tables/table6_q4.*`、`deliverables/final/paper/figures/q4/`、`deliverables/final/paper/figures/comparison/`、`deliverables/final/Q4_MANIFEST.json`、`docs/Q4_FINAL_FREEZE_AUDIT.md`。
- 校验：final workbook 无公式、四位小数格式、`result3=3449×22`、`result4=3185×22`；官方时间均为严格 60 s lattice；固定半径外部单元均为空；PCHIP 节点误差 `0`；全量候选校验 PASS。

## 最终边界

- Q3/Q4 已按批准完成 candidate→final byte copy；不改变 Q1/Q2，不启动新的 Q3/Q4 数值扩展。
- Q1 深谷文字保持 `pointwise error zero-crossing / cancellation dip`；Q2 失败历史目录继续保留。
- Q3/Q4 final-freeze audit 记录：`experiments/Q3_Q4_CANDIDATE/final_freeze_audit.json`；状态 `FINAL_FREEZE_COMPLETE`。
