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
| Q1 candidate 校验 | `scripts/validate_q1_candidate.py` | 已建立；只读、候选缺失时 fail-closed |
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
.\.venv\Scripts\python.exe scripts\validate_q1_candidate.py
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

当前 Q1 数值整改门为 `BLOCKED`，因此不生成 candidate 结果文件；若未来通过精度门，仍必须先运行 candidate 校验和格式/结构检查，并经人工确认后才能进入 final。上述数值实验只写入 `experiments/`，不写官方模板、不生成 `result1.xlsx`。
