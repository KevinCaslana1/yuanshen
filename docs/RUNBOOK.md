# Reproducibility Runbook

> 只记录已经建立或明确标记为未建立的运行信息。不编造不存在的入口、依赖或结果生成命令。

## Current Environment

- 默认 PATH Python：`3.8.10`，无 pip 且无 openpyxl，不能作为当前验证环境。
- 推荐 Python：`3.12.14`，使用 Codex bundled runtime 验证。
- Python 兼容范围：`>=3.8,<3.13`；尚未在所有 patch 版本上验证，不能宣称严格 patch 级复现。
- bundled bootstrap pip：`26.2.1`
- 当前项目 `.venv` pip：`25.0.1`；该版本由 `venv` 创建时随解释器提供，应用依赖仍由 requirements 文件固定
- 运行时依赖：见 `requirements.txt` 和 `requirements-dev.txt`。
- 当前校验脚本只读依赖：`openpyxl==3.1.5`。
- 测试依赖：`pytest==8.4.2`。
- 环境创建方式：使用 Python `venv`，不引入 Poetry、Conda 或 Docker。

## Established Entries

| 用途 | 程序入口 | 当前状态 |
|---|---|---|
| 官方输入资产检查 | `scripts/validate_inputs.py` | 已建立；只读 |
| 官方模板结构检查 | `scripts/validate_templates.py` | 已建立；只读 |
| 题目阅读 | `A题/A题.pdf` | 官方人工阅读材料 |
| 交付契约检查 | `scripts/validate_deliverable_contract.py` | 本阶段建立；只读 |
| Q1 最终输出精度审计 | `scripts/run_q1_final_accuracy.py` | 已建立；写入独立 EXP-Q1-FINAL-CONV 证据，不写工作簿 |
| Q1 数值制造解基准 | `scripts/run_q1_num_benchmark.py` | 已建立；隔离 benchmark，写入 EXP-Q1-NUM-BENCH，不读取生产输入、不写工作簿 |
| Q1 收敛诊断 | `scripts/run_q1_num_diag.py` | 已建立；比较相同物理时刻/位置，写入 Level 1–3、Richardson 和 SVG 定位图 |
| Q1 Picard 敏感性 | `scripts/run_q1_picard_sensitivity.py` | 已建立；比较 `1e-6/1e-8/1e-10`，写入 EXP-Q1-PICARD-SENS |
| Q1 BDF2 整改候选 | `scripts/run_q1_num_remediation.py` | 已建立；比较 M1-NUM-T2 与 BE，不生成 `result1.xlsx` |
| Q1 初始层诊断 | `scripts/run_q1_initial_layer.py` | 已建立；只运行 0–10 s 相容性、空间/时间梯和扩散尺度诊断 |
| Q1 BDF2 启动对照 | `scripts/run_q1_bdf2_startup.py` | 已建立；标准启动与早期 BE 子步对照，不生成工作簿 |
| Q1 表面误差衰减 | `scripts/run_q1_surface_decay.py` | 已建立；1–100 s 表面空间误差和 SVG 图 |
| Q1 聚类 benchmark | `scripts/run_q1_cluster_benchmark.py` | 已建立；独立制造解的非均匀保守 FVM benchmark |
| Q1 聚类短时对照 | `scripts/run_q1_cluster_short.py` | 已建立；真实 Q1 0–10 s 均匀/聚类网格对照 |
| Q1 聚类时间与舍入认证 | `scripts/run_q1_cluster_temporal.py` | 已建立；t=1 全官方节点空间/时间误差与半单位阈值认证 |
| Q1 全时域空间收敛 | `scripts/run_q1_full_horizon_validation.py` | 已建立；3 层边界聚簇空间层级，写入 `EXP-Q1-FULL-SPATIAL/` |
| Q1 全时域时间收敛 | `scripts/run_q1_full_horizon_validation.py` | 已建立；3 层 BDF2 时间层级，写入 `EXP-Q1-FULL-TEMPORAL/` |
| Q1 生产配置冻结双跑 | `scripts/run_q1_freeze_run.py` | 已建立；只写 `experiments/Q1_FREEZE_RUN/`，保存完整内部输出和确定性证据 |
| Q1 candidate 生成 | `scripts/generate_q1_candidate_from_freeze.py` | 已建立；只消费 `Q1_FREEZE_RUN/run_1`，写入 candidate，不写 final |
| Q1 candidate 校验 | `scripts/validate_q1_candidate.py` | 已建立；只读、候选缺失时 fail-closed |
| Q1 final 工作簿校验 | `scripts/validate_q1_final.py` | 已建立；只读，检查 final 结构、格式、轴、有限值、模板哈希和 candidate/final 哈希 |
| Q1 图表生成 | `scripts/generate_q1_figures.py` | 已建立；只读取冻结内部输出和收敛证据，写入 `figures/q1/`，不运行 solver |
| Q1 图表校验 | `scripts/validate_q1_figures.py` | 已建立；检查图表资产、源哈希、纸面追踪点和随机图表数据点 |
| 自动测试 | `pytest -q` | 本阶段建立；不包含模型测试 |

## Setup and Validation Commands

```powershell
<python-3.12> -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts\validate_inputs.py
.\.venv\Scripts\python.exe scripts\validate_templates.py
.\.venv\Scripts\python.exe scripts\validate_deliverable_contract.py
.\.venv\Scripts\python.exe scripts\run_q1_final_accuracy.py
.\.venv\Scripts\python.exe scripts\run_q1_num_benchmark.py
.\.venv\Scripts\python.exe scripts\run_q1_num_diag.py
.\.venv\Scripts\python.exe scripts\run_q1_picard_sensitivity.py
.\.venv\Scripts\python.exe scripts\run_q1_num_remediation.py
.\.venv\Scripts\python.exe scripts\run_q1_initial_layer.py
.\.venv\Scripts\python.exe scripts\run_q1_bdf2_startup.py
.\.venv\Scripts\python.exe scripts\run_q1_surface_decay.py
.\.venv\Scripts\python.exe scripts\run_q1_cluster_benchmark.py
.\.venv\Scripts\python.exe scripts\run_q1_cluster_short.py
.\.venv\Scripts\python.exe scripts\run_q1_cluster_temporal.py
.\.venv\Scripts\python.exe scripts\validate_q1_candidate.py
.\.venv\Scripts\python.exe scripts\run_q1_full_horizon_validation.py
.\.venv\Scripts\python.exe scripts\run_q1_freeze_run.py
.\.venv\Scripts\python.exe scripts\generate_q1_candidate_from_freeze.py
.\.venv\Scripts\python.exe scripts\validate_q1_final.py --output experiments/Q1_FINAL_FREEZE/final_result1_validation.json
.\.venv\Scripts\python.exe scripts\generate_q1_figures.py
.\.venv\Scripts\python.exe scripts\validate_q1_figures.py
.\.venv\Scripts\python.exe -m pytest -q
```

其中 `<python-3.12>` 表示已安装的 Python 3.12 解释器路径；不要把 `D:\python.exe` 这个无 pip 的 Python 3.8.10 当作冻结环境。

仓库当前为 Public；GitHub CI 不是本地 Gate 的依赖，但仓库同步本身是任务完成闭环的一部分。未来任务不得因仓库为 Public 而跳过推送；永久同步规则和失败处理见 `docs/GITHUB_SYNC_POLICY.md`。历史文档中出现的 `LOCAL COMMIT ONLY` / `DO NOT PUSH` 仅是当时阶段的审计事实，不再适用于未来任务。

## Mandatory GitHub Sync Policy

每项任务在交付前按以下顺序完成：

1. 运行必要验证，检查 `A题/`、`data/raw/` 和其他冻结路径未被修改；扫描敏感信息并检查 staged diff。
2. `git add -A` 后创建语义化 commit。
3. `git fetch origin`，检查 `git rev-list --left-right --count origin/main...HEAD`；远端 ahead 或发生 divergence 时 fail-closed。
4. 通过后执行普通 `git push origin main`，不使用 force、reset、rebase 或历史改写。
5. 执行 `git lfs push --all origin main` 与 `git lfs fsck`，再执行 `git push origin --tags` 同步正式标签。
6. 比较 `git rev-parse HEAD` 与 `git ls-remote origin refs/heads/main`，确认 `git status --short` 为空。

任务只有在验证、commit、普通 push、LFS 检查、标签同步和远端 SHA 校验均成功后才算 GitHub 同步完成。若 push 失败，保留本地提交和错误信息，并报告 `WORK COMPLETE / GITHUB SYNC FAILED`，不得改用危险 Git 操作。

## Q2 Design Gate Audit

Q2 当前只允许执行设计阶段的只读审计：

```powershell
.\.venv\Scripts\python.exe scripts\audit_q2_property_spec.py
.\.venv\Scripts\python.exe scripts\audit_q2_environment_tail.py
```

两条命令分别写入 `experiments/EXP-Q2-PROPERTY-POINTS/metrics.json` 和 `experiments/EXP-Q2-ENV-TAIL/metrics.json`；它们不调用 Q2 solver、不修改 `A题/`、不生成 `result2.xlsx`。Q2 正式执行顺序必须等人工授权，并先审查 `docs/Q2_PLAN.md` 中的环境、边界、终点、界面平均和精度门开放项。未来 solver 入口、长时运行、checkpoint 和 result2 生成顺序均保持 `NOT ESTABLISHED`。

## Future Entries

- 数据清洗入口：`NOT YET ESTABLISHED`
- 模型程序入口：`NOT YET ESTABLISHED`
- 实验运行命令：`NOT YET ESTABLISHED`
- 结果生成命令：`NOT YET ESTABLISHED`
- 数值结果验证命令：`NOT YET ESTABLISHED`
- 完整复现顺序：环境安装 → 输入校验 → 模板校验 → 交付契约校验 → Workflow 测试；模型和结果生成顺序仍为 `NOT YET ESTABLISHED`

## Official Template Delivery

1. 读取 `A题/附件/附件3/result1.xlsx` 至 `result4.xlsx`，不直接写入。
2. 将所需模板复制到 `deliverables/candidate/`。
3. 生成程序只允许写入 candidate 副本。
4. 运行结构、数值和格式验证。
5. 通过人工确认后复制到 `deliverables/final/`。

当前 Q1 全时域数值门和冻结双跑已通过，candidate `deliverables/candidate/result1.xlsx` 已生成并通过结构/格式/追踪验证；人工批准后已 COPY ONLY 到 `deliverables/final/result1.xlsx`，并通过 final 工作簿校验。图表生成器只消费冻结内部输出和已登记收敛证据，不重新运行 solver；所有实验与图表只写入各自隔离目录，官方模板 `A题/` 保持只读。

本轮初始层/表面精度诊断的可复现顺序为：先运行 `run_q1_initial_layer.py`，再运行 `run_q1_bdf2_startup.py`、`run_q1_surface_decay.py`、`run_q1_cluster_benchmark.py`、`run_q1_cluster_short.py` 和 `run_q1_cluster_temporal.py`。最后一个脚本会写出 `reference_t1_official_values` 与 `rounding_certification`；其结果只覆盖短时候选审计，不替代 0–1800 s 全网格最终门。

全时域冻结顺序：运行 `run_q1_full_horizon_validation.py`；确认两个 full-horizon metrics 的 criterion 通过后，运行 `run_q1_freeze_run.py`（创建一次 `Q1_FREEZE_RUN` 并内部双跑）；最后运行 `generate_q1_candidate_from_freeze.py`。人工批准后只允许将 candidate 字节复制到 `deliverables/final/`，随后运行 `validate_q1_final.py`、`generate_q1_figures.py` 和 `validate_q1_figures.py`，并把清单、审计和验证报告纳入本地提交。当前 Q1 已完成该流程；不得重新运行 solver 或启动 Q2，除非获得新的明确授权。

## Q2 Human Decision Packet

决策证据入口：`docs/Q2_HUMAN_DECISION_PACKET.md`。当前只允许审核和小规模
decision-target runs，不允许生成 `result2.xlsx` 或 candidate/final workbook。

```powershell
.\.venv\Scripts\python.exe scripts\run_q2_decision_targets.py boundary-long
.\.venv\Scripts\python.exe scripts\run_q2_decision_targets.py interface-long
.\.venv\Scripts\python.exe -m pytest -q
```

`boundary-long` 是 `dt=2 s` 的定向 h/hm 影响筛查；`interface-long` 使用 canonical
`n=80, dt=.25 s` 长时检查点。两者都只写 `experiments/EXP-Q2-021-DECISION-TARGETS/`
的 JSON/CSV/compact diagnostics，不写 workbook。canonical consumer 必须经由
`src.q2.lineage.canonical_path` 或 `canonical_csv_path`；默认 hash verification
开启，raw duplicate 文件被拒绝。

## Q2 Production Freeze Run（2026-09-12）

人工批准后，冻结基线和配置，执行：

```powershell
.\\.venv\\Scripts\\python.exe scripts\\run_q2_production_freeze.py
.\\.venv\\Scripts\\python.exe scripts\\build_q2_production_manifest.py
.\\.venv\\Scripts\\python.exe scripts\\run_q2_accuracy_confirmation.py
```

本次生产双跑和独立参考均已完成，但 `accuracy_confirmation.json` 为 `FAIL`。因此以下命令被故意阻止：

```powershell
node scripts\\build_q2_candidate.mjs
.\\.venv\\Scripts\\python.exe scripts\\validate_q2_candidate.py
.\\.venv\\Scripts\\python.exe scripts\\generate_q2_figures.py
```

候选工作簿只有在 field L∞/L2、时间/空间参考、事件邻域、结构/格式/溯源和确定性全部 PASS 后才可生成；任何改变 post-14400 环境规则、dt/grid 或内部精度门的动作都必须先获得新的人工授权。该段所述“只允许本地审计提交、不推送远端”仅保留为 Q2 accuracy gate 失败阶段的历史事实；自 2026-09-12 起，未来任务按本 Runbook 前述永久同步政策执行。

### Authorized V3 completion

本次实际使用的新目录 `experiments/Q2_FREEZE_RUN_V3/`，按顺序完成：

```powershell
.\.venv\Scripts\python.exe scripts\finalize_q2_v3_run1_and_run2.py
.\.venv\Scripts\python.exe scripts\audit_q2_v3_postproduction.py
.\.venv\Scripts\python.exe scripts\update_q2_v3_manifest.py
.\.venv\Scripts\python.exe scripts\build_q2_v3_candidate_streaming.py
.\.venv\Scripts\python.exe scripts\validate_q2_v3_candidate.py
.\.venv\Scripts\python.exe scripts\generate_q2_v3_figures.py
.\.venv\Scripts\python.exe scripts\validate_q2_v3_figures.py
```

artifact-tool 已先按技能要求尝试；因该超大工作簿在 4 GB 和 8 GB V8 heap 均 OOM，最终使用 `openpyxl.Workbook(write_only=True)` 流式 fallback。Q2 已获人工 freeze approval，final 阶段仅允许将已验证 candidate 与已验证 PNG/SVG 执行 COPY ONLY；不得重新计算、重新绘图或直接启动 Q3/Q4。冻结记录见 `experiments/Q2_FINAL_FREEZE/freeze_record.json`。

## Q4 Numerical Convergence Finalization（2026-09-13）

本节记录 Q4 数值收敛终结审计的可复现入口。命令使用独立审计实现，从 `t=0` 运行新层级；只写入 `experiments/Q4_CONVERGENCE_FINAL/`，不调用或修改 `src/q4/`，不修改冻结工作簿和 final 交付物。

```powershell
.\.venv\Scripts\python.exe scripts\run_q4_convergence_final.py
.\.venv\Scripts\python.exe scripts\build_q4_error_decomposition.py
.\.venv\Scripts\python.exe scripts\run_q4_next_refinement.py
.\.venv\Scripts\python.exe scripts\run_q4_interpolation_sensitivity_final.py
.\.venv\Scripts\python.exe scripts\build_q4_error_decomposition.py
```

当前证据：A/B/C/D/E 已完成；空间项主导，PCHIP 保留，保守不确定度 `0.0806158781 h` 超过 `0.00005 h`，故 `Q4 NUMERICAL CONVERGENCE = HOLD`。未创建 corrected candidate，不得修改 `deliverables/final/result4.xlsx`。

## Q4 Spatial Convergence Extrapolation（2026-09-13）

本节记录连续空间极限 gate 的可复现入口。所有新增层级固定 `dt=2 s`，从 `t=0` 独立运行；非等比网格直接拟合 `t(n)=t_inf+a*n^(-p)`，不使用固定 refinement ratio 的简化 Richardson 公式。命令只写入 `experiments/Q4_SPATIAL_CONVERGENCE_FINAL/`，不修改 `src/q4/` 或冻结交付。

```powershell
.\.venv\Scripts\python.exe scripts\run_q4_spatial_n256_dt2.py 256
.\.venv\Scripts\python.exe scripts\run_q4_spatial_n256_dt2.py 320
.\.venv\Scripts\python.exe scripts\fit_q4_spatial_continuum.py
.\.venv\Scripts\python.exe scripts\run_q4_spatial_n256_dt2.py 384
.\.venv\Scripts\python.exe scripts\fit_q4_spatial_continuum.py
```

当前证据：四组 triplet 的 `t_inf` 最近差为 `0.0007180914 h`，p 仍漂移，故 `Q4 CONTINUUM CONVERGENCE = HOLD`；暂缓 `dt=1 s` 和二维外推，不自动跳到 `n=512`，不得创建 corrected candidate 或修改 `deliverables/final/result4.xlsx`。

## Q4 Final Asymptotic Certification（2026-09-13）

最终 gate 已授权的最小新增运行和后处理顺序如下。`n=512`、`n=384,dt=1` 均从 `t=0` 完整运行；只写入隔离实验目录，不修改 `src/q4/`、冻结 workbook 或 final 图表。

```powershell
.\.venv\Scripts\python.exe scripts\run_q4_spatial_n256_dt2.py 512
.\.venv\Scripts\python.exe scripts\fit_q4_final_asymptotic.py
.\.venv\Scripts\python.exe scripts\run_q4_temporal_n384_dt1.py
.\.venv\Scripts\python.exe scripts\build_q4_final_certification.py
```

当前证据：free-p、fixed-p=2、p=2+n^-3 方法和 supporting temporal order 已记录；audit estimate=`52.6575227799 h`，保守总不确定度=`60.9467 s`，高于插值敏感性，故 `Q4 FINAL NUMERICAL CERTIFICATION = HOLD`。不运行 `n=640` 或 `dt=0.5`，不创建 corrected candidate。

## Q4 Deadline Fast-Final Production（2026-09-13）

最新人工 gate 仅允许以下两个 fresh-from-`t=0` 运行：

```powershell
.\.venv\Scripts\python.exe scripts\run_q4_paper_final.py --n 640 --output experiments\Q4_PAPER_FINAL_N640 --minimal
.\.venv\Scripts\python.exe scripts\run_q4_paper_final.py --n 768 --output experiments\Q4_PAPER_FINAL_N768
.\.venv\Scripts\python.exe scripts\build_q4_n768_delivery.py
.\.venv\Scripts\python.exe scripts\generate_q4_n768_figures.py
.\.venv\Scripts\python.exe scripts\generate_q4_n768_table_package.py
.\.venv\Scripts\python.exe scripts\validate_q4_n768_candidate.py
.\.venv\Scripts\python.exe scripts\finalize_q4_n768_freeze.py
```

L 的 `official_samples_with_endpoint_raw.csv` 是 workbook/Table6/论文图表的 canonical source；后处理不得再次调用 solver。官方 result4 只保留 `60..floor(t4/60)*60` 的 60 s lattice，精确 `t4` 只用于 Table6、审计和比较记录。完成后必须检查 Q1/Q2/Q3 hashes、`A题/`、`src/q2/`、历史失败实验、candidate/final 哈希、图 trace、Word/PDF 和全套测试。

当前结果：K=`52.6664021484 h`，L=`52.6640375959 h`，I→K→L 单调；L 已冻结为 Q4 PAPER FINAL。旧渐近 HOLD 章节是历史证据，不删除、不作为当前生产入口。
