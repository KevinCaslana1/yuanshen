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
- 当前阶段不创建、不填写 candidate 或 final 结果文件。
