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

仓库当前为 Public。此阶段不将 GitHub CI 作为 Gate 依赖，按本 Runbook 在本地执行全部校验即可。

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
