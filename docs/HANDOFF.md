# Handoff

> 本文件保持很短，只服务于新会话、上下文压缩或其他 Agent 的快速接管。

## 当前做到哪里

已完成 Workflow Hardening / Problem Registration；尚未开始建模。

## 刚刚完成什么

已登记 2026 高教社杯 A题、官方资产哈希、Q1-Q4、输入/模板校验脚本和 candidate/final 交付隔离流程。

## 当前最好结果

无真实实验结果。

## 当前主要决策

`A题/` 是 OFFICIAL_SOURCE / IMMUTABLE_SOURCE。正式结果只能从官方模板复制到 `deliverables/candidate/` 后生成。

## 不要重复尝试什么

尚无失败路线；不要在人工批准前进入 Q1-Q4 建模，不要修改官方 result 模板，不要虚构实验或结果。

## 下一步

等待人工确认 Hardening 审计；确认后再建立明确授权的建模任务。

## 重点阅读文件

`AGENTS.md`、`docs/PROBLEM_SPEC.md`、`docs/DATA_CATALOG.md`、`docs/STATE.md`、`docs/TODO.md`、`docs/RUNBOOK.md`、`docs/VALIDATION.md`。

## 风险与注意事项

官方资产位于 `A题/`，必须保持只读。当前只建立 Workflow 与验证基础设施；Python 依赖和完整复现环境尚未固定。Git 的 `main` 已与 `origin/main` 同步。
