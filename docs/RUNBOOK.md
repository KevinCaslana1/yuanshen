# Reproducibility Runbook

> 只记录已经建立或明确标记为未建立的运行信息。不编造不存在的入口、依赖或结果生成命令。

## Current Environment

- Python：已用 Codex bundled runtime 验证为 `3.12.14`
- 环境创建方式：`NOT YET ESTABLISHED`
- 依赖安装方法：`NOT YET ESTABLISHED`
- 当前校验脚本依赖：Python 标准库与运行环境中的 `openpyxl`（仅只读检查 XLSX）
- 依赖版本锁定：`NOT YET ESTABLISHED`

## Established Entries

| 用途 | 程序入口 | 当前状态 |
|---|---|---|
| 官方输入资产检查 | `scripts/validate_inputs.py` | 已建立；只读 |
| 官方模板结构检查 | `scripts/validate_templates.py` | 已建立；只读 |
| 题目阅读 | `A题/A题.pdf` | 官方人工阅读材料 |

## Future Entries

- 数据清洗入口：`NOT YET ESTABLISHED`
- 模型程序入口：`NOT YET ESTABLISHED`
- 实验运行命令：`NOT YET ESTABLISHED`
- 结果生成命令：`NOT YET ESTABLISHED`
- 数值结果验证命令：`NOT YET ESTABLISHED`
- 完整复现顺序：`NOT YET ESTABLISHED`

## Official Template Delivery

1. 读取 `A题/附件/附件3/result1.xlsx` 至 `result4.xlsx`，不直接写入。
2. 将所需模板复制到 `deliverables/candidate/`。
3. 生成程序只允许写入 candidate 副本。
4. 运行结构、数值和格式验证。
5. 通过人工确认后复制到 `deliverables/final/`。

当前阶段只建立上述 Workflow，不生成 candidate 结果文件。
