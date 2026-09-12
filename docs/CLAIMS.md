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

Q2 已完成 V3 production candidate gate，但当前仍没有登记为论文 `VERIFIED` 的最终 Q2 主张。V3 Run1 的生产源、候选 workbook 和图表可用于后续人工批准后的论文取数；在批准前不得把 candidate 当作 final，不得把 passive bracket `[206935.0,206935.25] s` 当作 Q3 drying time，也不得把 formal-output certificate 写成 n=640 full-horizon proof。`14400.25 s` 只属于 `SUPPORTED_INTERNAL_TRANSITION_DIAGNOSTIC`。
