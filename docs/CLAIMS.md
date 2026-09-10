# Paper Claims Ledger

这里记录论文中的重要定量或定性主张，确保每条主张都能追溯到实际证据。

状态：`UNVERIFIED` / `VERIFIED` / `OUTDATED`。

## 主张索引

| ID | Claim | Evidence | Source | Figure/Table | Paper Section | Status |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | 尚无论文主张 |

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

