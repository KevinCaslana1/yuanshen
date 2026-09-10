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
| T-007 | P1 | 全局 | T-001 | TODO | `docs/RUNBOOK.md` | Python/依赖/复现环境经过人工确认并固定版本 | 1 个会话 |
| T-008 | P1 | 全局 | T-001 | TODO | 人工确认记录 | 确认题目事实分层、开放问题和官方资产哈希 | 15 分钟 |

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
