# Validation Checklist

本文件是独立验证清单。模型得到较好指标并不等于问题已经解决。

## Workflow Integrity Checks

| 检查项 | 方法 | 结果 | 证据 | 状态 |
|---|---|---|---|---|
| 官方资产存在性与可读取性 | `scripts/validate_inputs.py` | 7 个官方资产可读取 | 脚本输出 | PASS |
| 官方资产 SHA-256 | `scripts/validate_inputs.py` | 与 `docs/DATA_CATALOG.md` 一致 | DATA_CATALOG | PASS |
| 官方 Workbook Sheet 与行列骨架 | `scripts/validate_inputs.py` | 附件1/2与4个模板结构一致 | 脚本输出 | PASS |
| 官方结果模板完整性 | `scripts/validate_templates.py` | Sheet、表头、占位时间和数据区空白通过 | 脚本输出 | PASS |
| 官方源文件未被修改 | `git diff -- A题` | 无差异 | Git 状态 | PASS |
| 交付隔离 | 人工检查 `deliverables/README.md` | candidate/final 已建立，当前无结果文件 | 交付说明 | PASS |

## 通用检查

| 检查项 | 适用问题 | 结果 | 证据 | 状态 |
|---|---|---|---|---|
| 数据泄漏 | 全局 | 尚未检查 | — | TODO |
| 数据划分与交叉验证 | 全局 | 尚未检查 | — | TODO |
| 残差分析 | 视模型而定 | 尚未检查 | — | TODO |
| 异常值影响 | 全局 | 尚未检查 | — | TODO |
| 参数敏感性 | 全局 | 尚未检查 | — | TODO |
| 鲁棒性与稳定性 | 全局 | 尚未检查 | — | TODO |
| 边界情况 | 全局 | 尚未检查 | — | TODO |
| 与现实常识一致性 | 全局 | 尚未检查 | — | TODO |
| Baseline 对比 | Q1/Q2/Q3/Q4 | 尚未检查 | — | TODO |
| 必要的消融实验 | 视模型而定 | 尚未检查 | — | TODO |

## 验证记录模板

```markdown
## VAL-xxx 标题

问题：Q1/Q2/Q3/Q4
检查项：
方法：
结果：
证据：EXP-xxx / 文件路径
结论：
剩余风险：
状态：PASS / FAIL / PARTIAL / TODO
```
