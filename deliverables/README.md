# Deliverables Workflow

官方模板和最终交付物分离管理：

```text
A题/附件/附件3/result*.xlsx
        ↓ 复制
deliverables/candidate/result*.xlsx
        ↓ 程序写入 candidate 副本
结构验证 → 数值验证 → 格式验证 → 人工确认
        ↓
deliverables/final/result*.xlsx
```

规则：

- `A题/附件/附件3/result1.xlsx` 至 `result4.xlsx` 永远只读。
- 任何程序不得直接打开官方模板进行写入。
- `candidate/` 是可检查、可丢弃的候选结果区。
- 只有通过验证并获得人工确认的文件才能进入 `final/`。
- 当前 Q1 状态：`deliverables/candidate/result1.xlsx` 已通过候选校验，人工批准后已按 COPY ONLY 规则写入 `deliverables/final/result1.xlsx`；final 工作簿和 `Q1_MANIFEST.json` 已通过最终验证。Q2 V3 已获人工 freeze approval，`deliverables/candidate/result2.xlsx` 已按字节原样复制到 `deliverables/final/result2.xlsx`，并由 `Q2_MANIFEST.json` 和 `experiments/Q2_FINAL_FREEZE/freeze_record.json` 记录；Q3/Q4 未启动。
- 生成 Q1 图表时只读取冻结运行源，图表位于 `figures/q1/`，不修改工作簿或官方源。
