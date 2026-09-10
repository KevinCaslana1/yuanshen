# TODO

状态：`TODO` / `DOING` / `BLOCKED` / `DONE` / `CANCELLED`  
优先级：`P0` 必须完成，`P1` 重要，`P2` 可选优化，`P3` 有时间再做。

| Task ID | 内容 | 优先级 | 问题 | 依赖 | 状态 |
|---|---|---|---|---|---|
| T-001 | 提供并阅读正式赛题与附件 | P0 | 全局 | — | TODO |
| T-002 | 根据赛题拆分 Q1/Q2/Q3 与数据需求 | P0 | 全局 | T-001 | TODO |
| T-003 | 为各主要问题建立简单 Baseline | P1 | Q1/Q2/Q3 | T-002 | TODO |

## 任务记录模板

```text
T-xxx
内容：
Priority: P0/P1/P2/P3
问题：Q1/Q2/Q3/全局
Depends: T-xxx 或 —
Status: TODO/DOING/BLOCKED/DONE/CANCELLED
备注：
```

只新增会影响未来工作的任务；优先完成 P0/P1，不自行堆积大量 P2/P3。

