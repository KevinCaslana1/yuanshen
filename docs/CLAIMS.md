# Paper Claims Ledger

这里记录论文中的重要定量或定性主张，确保每条主张都能追溯到实际证据。

状态：`UNVERIFIED` / `VERIFIED` / `OUTDATED`。

## 主张索引

| ID | Claim | Evidence | Source | Figure/Table | Paper Section | Status |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | 尚无论文主张 |

Q1 candidate 的数值和论文表追踪已完成，人工 freeze approval、final 工作簿校验和可视化包也已完成。当前仍未新增 VERIFIED 论文主张；后续论文写作必须逐条从 `Q1_FINAL_FREEZE_AUDIT.md`、冻结实验和图表源数据登记可核验主张，不得把模型假设写成官方事实。

## 主张记录模板

```markdown
## C-xxx

Claim：
Evidence：EXP-xxx 与 EXP-xxx，或明确的计算过程
Source：结果文件的绝对/项目内路径
Figure/Table：
Paper：Section x.x
计算方式：
限制与适用范围：
Status：UNVERIFIED / VERIFIED / OUTDATED
```

重要数字不能由 Agent 猜测或“合理补全”。没有证据就保持 `UNVERIFIED`，并在 `TODO.md` 中建立任务。

## Q2 Boundary

Q2 当前仅完成设计 Gate 和只读输入审计，没有可登记的正式 Q2 论文主张。`EXP-Q2-PROPERTY-POINTS` 的公式点和 `EXP-Q2-ENV-TAIL` 的尾窗统计只用于实现前审计；不得据此宣称模型结果、环境充分性、耦合机制或 Q2 终点已经确定。
