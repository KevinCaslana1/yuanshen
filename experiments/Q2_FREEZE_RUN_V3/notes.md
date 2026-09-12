# Q2 V3 Production Freeze Run Notes

日期：2026-09-12

授权：`Q2 V3 FREEZE RUN AUTHORIZATION = APPROVED`

## Scope

本目录记录唯一允许进入 Q2 candidate 的 V3 生产双跑。Run1 与 Run2 均从官方 t=0 初值 fresh start，未复用旧 checkpoint、field 或数据。Run1 是 `PRODUCTION_CANONICAL`，Run2 是 `DETERMINISM_REFERENCE`。

## Frozen configuration

- n=320、cluster_power=3、harmonic interface mean
- early `dt=0.015625 s` through exactly 5 s；production `dt=0.25 s`
- BE startup/BDF2；5 s step change 与 exact `t=14400 s` 均按认证策略 BE restart
- Attachment 1 在 `0..14400 s` 分段线性；之后 ENV-B 常值 `49.99525 °C / 0.049988 kg/kg`
- passive observer threshold `max(C)-0.15`；bracket `[206935.0,206935.25] s`
- final horizon `ceil(t_high)+21600=228536 s`

## Results

两次 raw internal source、官方整数秒 sampled source 和 diagnostics byte/hash identical；Run1 共 228536 个时间步，non-converged=0，Picard 迭代为 2–3。t=0 只保留在 raw internal output；正式 source 为 Run1 `official_samples.csv`。

candidate workbook、figure package 和所有门禁证据已通过验证，但当前交付状态仍是 `VALIDATED CANDIDATE / WAITING FOR HUMAN Q2 FREEZE APPROVAL`。不得自动复制到 `deliverables/final/`，不得启动 Q3/Q4。

## Reproduction and provenance

主运行入口：`scripts/run_q2_v3_production.py`；Run1/Run2 完成后的后处理入口：`scripts/finalize_q2_v3_run1_and_run2.py`。V3 source hashes 和 production lock 见 `code_hashes.json`；正式 source lineage 见 `lineage.json`、`experiments/Q2_CANONICAL_DATA_MANIFEST.json`。错误 horizon、preflight 和 postprocess failure attempts 均在相邻目录保留，均非交付来源。
