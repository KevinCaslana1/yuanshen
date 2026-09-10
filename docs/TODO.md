# TODO

状态：`TODO` / `DOING` / `BLOCKED` / `DONE` / `CANCELLED`  
优先级：`P0` 必须完成，`P1` 重要，`P2` 可选优化，`P3` 有时间再做。

每项任务只有在 `Acceptance Criteria` 全部满足后才能标记 `DONE`。

| Task ID | Priority | Question | Depends | Status | Expected Artifact | Acceptance Criteria | Timebox |
|---|---|---|---|---|---|---|---|
| T-001 | P0 | 全局 | — | DONE | `docs/PROBLEM_SPEC.md` | A题事实、Q1-Q4、输入输出和未决项均已分层登记，未写建模方案 | 本轮 |
| T-002 | P0 | 全局 | T-001 | DONE | `docs/DATA_CATALOG.md` | 7 个官方资产均有路径、类型、大小、SHA-256、结构与保护状态 | 本轮 |
| T-003 | P0 | 全局 | T-001 | DONE | `AGENTS.md`, `problem/README.md` | `A题/` 被声明为不可写官方源，禁止复制出第二个原始数据源 | 本轮 |
| T-004 | P0 | Q1-Q4 | T-002 | DONE | `src/q4/`, `docs/STATE.md`, `docs/VALIDATION.md` | Q1、Q2、Q3、Q4 均已注册，模板不再只支持 Q1-Q3 | 本轮 |
| T-005 | P0 | 全局 | T-002 | DONE | `scripts/validate_inputs.py`, `scripts/validate_templates.py` | 输入存在性、哈希、Sheet、行列骨架和模板空白完整性检查可执行 | 本轮 |
| T-006 | P1 | 全局 | T-005 | DONE | `deliverables/README.md` | 官方模板到 candidate、验证、人工确认、final 的隔离流程已建立 | 本轮 |
| T-007 | P1 | 全局 | T-001 | DONE | `requirements.txt`, `requirements-dev.txt`, `docs/RUNBOOK.md` | Python 兼容范围、pip、openpyxl、pytest、安装和验证命令已记录；当前 `.venv` 可运行 | 1 个会话 |
| T-008 | P1 | 全局 | T-001 | DONE | 人工审查前置条件 | 仓库、官方资产、题目事实和当前状态无新不一致 | 15 分钟 |
| T-009 | P0 | 全局 | T-007 | DONE | `.venv` | 独立环境安装 requirements 成功，版本可读 | 本轮 |
| T-010 | P0 | 全局 | T-002 | DONE | `docs/DELIVERABLE_SPEC.md`, `config/deliverables.json` | result1-result4 的模板、路径、单位、采样、精度、骨架/最终形状状态已登记 | 本轮 |
| T-011 | P0 | 全局 | T-010 | DONE | `scripts/validate_deliverable_contract.py` | JSON 与 Markdown 契约、路径、Sheet、单位、精度、Open Question 状态检查通过 | 本轮 |
| T-012 | P0 | 全局 | T-011 | DONE | `tests/` | 12 个 Workflow 测试通过；不包含模型测试 | 本轮 |
| T-013 | P0 | 全局 | T-012 | DONE | `docs/VALIDATION.md` | Pre-Modeling Gate 所有必要项已审计并标记 PASS | 本轮 |

## 任务记录模板

```text
T-xxx
Task ID:
Priority: P0/P1/P2/P3
Question: Q1/Q2/Q3/Q4/全局
Depends: T-xxx 或 —
Status: TODO/DOING/BLOCKED/DONE/CANCELLED
Expected Artifact:
Acceptance Criteria:
Timebox:
备注：
```

只新增会影响未来工作的任务；优先完成 P0/P1，不自行堆积大量 P2/P3。
