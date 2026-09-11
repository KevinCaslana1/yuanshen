# Failures

## F-Q1-002 — EXP-003 comparison helper rejected valid different time histories

- **Status:** FIXED
- **Observed:** The first EXP-003 run stopped before writing evidence because the comparison helper required the two runs to have the same number of stored snapshots. Different time steps necessarily produce different history lengths.
- **Cause:** The helper only needs matching final times for the requested final-field sensitivity comparison, but it checked both history length and final time.
- **Fix:** Relaxed the check to require matching final times only. Re-ran the affected experiment from EXP-003 after the fix.
- **Impact:** No official source, deliverable workbook, or experiment evidence was overwritten; the failed attempt produced no evidence directory.
- **Reproducibility:** The failed command was `.\\.venv\\Scripts\\python.exe scripts\\run_q1_experiments.py EXP-003` at implementation commit `ff9a4a759cb6143aaef19c5bec9074449d78e44c`.

这里只记录未来值得知道、能够避免重复踩坑的失败，不记录普通语法错误或一次性调试输出。

## 失败索引

| ID | 实验 | 方法 | 现象 | 最终判断 | 重试条件 |
|---|---|---|---|---|---|
| F-Q1-001 | EXP-001 | 直接执行 `scripts/run_q1_smoke.py` | `ModuleNotFoundError: No module named 'src'` | 入口脚本缺少项目根目录路径注入，已修复；不是数值失败 | 修复后重新运行 EXP-001 |
| F-Q1-003 | EXP-Q1-FINAL-CONV | 完整输出网格四位小数稳定性 | N160→N320 与 dt1→dt0.25 仍有大量报告值变化 | 当前精度门阻塞；不是求解器崩溃，也不授权放宽门槛 | 人工决定数值整改方案后重跑完整门 |
| F-Q1-004 | EXP-Q1-NUM-BENCH | 制造解基准初版 | 测试边界环境导数漏乘 `e^{-t}`，导致初版误差不代表生产实现 | 已修正基准源项/Robin 环境表达式，并从 `843d628` 重跑；不是生产代码缺陷 | 保留修正后的 benchmark 证据 |
| F-Q1-005 | EXP-Q1-NUM-REMEDIATION | BDF2 候选的完整网格安全裕量 | 论文点已稳定，但 BDF2 `dt=0.5→0.25 s` 的全网格含水率 L∞ 差 `0.0011151`，Richardson 剩余估计 `0.0006163`，超过四位小数半单位 | 候选有效改善但不能冻结为最终配置 | 人工审查是否做针对早期/表面误差的最小附加诊断 |
| F-Q1-006 | EXP-Q1-SURFACE-DECAY | 初版误将不同空间与时间步长混合为表面空间误差 | 误差不再代表单一离散维度 | 已改为 N320/N640/N1280 共同 dt=.0625 s；dt=.03125 仅作时间分辨率上下文 | 保持同一离散维度比较 |
| F-Q1-007 | EXP-Q1-CLUSTER-TEMPORAL | 初版参考键切片混入空间/时间比较，且未覆盖 base320 空间层级 | Richardson 参考不具备同一网格/同一物理时刻的可解释性 | 改为显式空间键和显式时间键，并加入 base320/base640/base1280 dt=.03125 | 任何新收敛脚本禁止依赖字典顺序切片 |
| F-Q1-008 | EXP-Q1-SURFACE-DECAY audit | 初次审计脚本将字面表面标签与近表面标签混用，且旧 helper 只保存绝对误差 | 首次长时运行在写完短时表后因标签 KeyError 停止；不能证明数值失败 | 统一位置标签；所有审计数据同时保存 signed/absolute，补充直接 signed 图与 semilogy 图后完整重跑通过 | 保持 signed/absolute 字段并显式检查位置映射 |

## 失败记录模板

```markdown
## F-xxx 标题

对应实验：EXP-xxx
方法：
现象：
失败原因：
已尝试修复：
最终判断：
是否放弃：是/否
重新尝试条件：
```

## F-Q1-001 Q1 smoke 入口路径缺失

对应实验：EXP-001

方法：使用 `.venv` 直接执行 `scripts/run_q1_smoke.py`。

现象：Python 无法导入项目包 `src`。

失败原因：直接执行脚本时，解释器的模块搜索路径未自动包含项目根目录。

已尝试修复：在脚本启动处显式加入脚本父目录对应的项目根目录。

最终判断：这是启动入口缺陷，不是 Q1 方程、离散或求解器数值失败。

是否放弃：是，作为本次入口修复后的历史故障保留。

重新尝试条件：修复后重新运行 EXP-001，并确认后续正式实验只能在 smoke PASS 后启动。

## F-Q1-003 Q1 最终输出级数值精度门阻塞

对应实验：EXP-Q1-FINAL-CONV

方法：固定 M1、线性边界输入、Robin 边界和 Picard 收敛参数；空间依次测试 `N=80/160/320`（`dt=0.25 s`），时间依次测试 `dt=1/0.5/0.25 s`（固定 `N=320`）。每次比较完整 `1800×21` 交付网格和论文 `7×5` 追踪点，分别检查原始差异与 `ROUND_HALF_UP` 四位小数后的单元格稳定性。

现象：空间最细比较 N160→N320 的完整网格仍有温度 `1398/37800`、水分 `4468/37800` 个四位小数差异；时间最细比较 dt1→dt0.25 的完整网格仍有温度 `36498/37800`、水分 `6926/37800` 个差异。论文点也未全量稳定。

失败原因：在当前已测试内部网格和时间步长序列下，输出级四舍五入结果未达到“所有单元稳定”的交付门槛。该结果只说明测试配置未通过，不证明模型方程或求解器必然错误。

已尝试修复：已完成空间细化至 `N=320` 和时间细化至 `dt=0.25 s` 的门控比较；没有修改容差、交付契约或官方资产。

最终判断：Q1 最终数值准确性门 `BLOCKED`；不生成 candidate/final `result1.xlsx`，不执行 `Q1_FREEZE_RUN`，不启动 Q2。

是否放弃：否。

重新尝试条件：人工审查数值整改方案并明确允许的模型/离散调整后，重新登记并运行新的唯一实验编号；不得仅放宽四舍五入稳定性标准。

## F-Q1-004 制造解基准初版边界表达式错误

对应实验：EXP-Q1-NUM-BENCH

方法：对独立制造解 `u(r,t)=e^{-t}(1+r^4)` 使用同一径向有限体积空间装配和 Thomas 求解器，检查 Robin 边界与空间/时间阶数。

现象：基准初版的 Robin 环境导数项漏掉 `e^{-t}` 因子，造成边界残差被误计入离散误差。

失败原因：制造解验证脚本中的解析边界环境表达式书写错误；生产 `src/q1/` 代码未使用该表达式。

已尝试修复：修正基准脚本中的环境函数后重新运行；修正后 BE 空间 L∞ 阶为 `1.9715, 1.9938, 1.9985`，时间 L∞ 阶为 `1.0096, 1.0146, 1.0089`。

最终判断：这是隔离验证 harness 的失败，不是生产模型失败；修正后的 benchmark 才是正式证据。

是否放弃：是，初版输出不作为证据；修正后的实验保留。

重新尝试条件：若生产装配或边界形式变化，必须重新运行独立制造解 benchmark。

## F-Q1-006 表面衰减实验初版混合空间/时间误差

对应实验：`EXP-Q1-SURFACE-DECAY`

方法：初版同时改变空间网格和时间步长来比较 N640 与 N1280，不能将差异唯一归因于空间离散。

现象：所得表面差异混合了空间误差和时间误差，不能直接支持初始层的空间衰减判断。

失败原因：实验设计没有固定非比较维度。

已尝试修复：改为 N320/N640/N1280 均使用 `dt=0.0625 s` 的同时间步空间梯；N1280 `dt=0.03125 s` 只保留为时间分辨率上下文。

最终判断：修正后的 `EXP-Q1-SURFACE-DECAY` 才作为证据。

是否放弃：是，初版混合比较不作为证据。

重新尝试条件：所有空间收敛比较固定同一时间步，所有时间收敛比较固定同一空间网格。

## F-Q1-007 聚类时间实验初版参考层级不明确

对应实验：`EXP-Q1-CLUSTER-TEMPORAL`

方法：初版用字典顺序切片推断参考键，并未同时纳入 base320/base640/base1280 的同一时间步空间层级。

现象：空间与时间 Richardson 差异可能混入不同离散维度，且无法生成完整官方输出节点的 t=1 误差表。

失败原因：参考层级隐含依赖键顺序，实验脚本缺少显式比较契约。

已尝试修复：使用显式空间键和显式时间键，增加聚类 base320/base640/base1280、`dt=0.03125 s` 空间梯，并对全部 21 个官方位置分别计算空间/时间剩余误差和舍入状态。

最终判断：修正后的 `EXP-Q1-CLUSTER-TEMPORAL` 才作为证据。

是否放弃：是，初版参考计算不作为证据。

重新尝试条件：新实验必须显式列出 coarse/fine/reference 键，禁止依赖字典顺序切片。

## F-Q1-008 表面误差审计 harness 初次标签与误差字段问题

对应实验：`EXP-Q1-SURFACE-DECAY`、`EXP-003`、`EXP-004`

方法：执行新的 Q1 表面 signed-error、边界轨迹和分离收敛审计。

现象：首次长时审计在 N640/N1280 短时对照、原始表和时间收敛运行完成后，因脚本把 `surface_2.0cm` 与收敛表使用的 `surface` 混用而触发 `KeyError`；同时审计发现历史表面 helper 只持久化了 `abs(C_test-C_ref)`，不满足 signed-error 复核契约。

失败原因：实验 harness 的位置标签契约不统一，且旧误差输出接口没有同时保留 signed 字段。这不是生产 `src/q1` 求解器的数值失败。

已尝试修复：统一位置标签为 `surface`、`near_surface_1.9cm`、`r_1.5cm`、`r_1.0cm`、`center`；更新旧表面 helper 保留 `r1.9cm_signed`/`r2.0cm_signed`；新审计脚本同时写出 signed/absolute 原始 CSV、signed 线性图和 absolute semilogy 图，并显式记录无 smoothing、无 error interpolation、无 epsilon clip 和 x/y 对齐检查。修复后完整审计重跑成功。

最终判断：这是已修复的实验记录/可观测性缺陷，不是 Q1 数值算法 bug；最终诊断由修复后的完整证据决定。

是否放弃：是，首次中断运行和只含绝对误差的旧输出不作为本轮诊断证据；修复后的实验产物保留。

重新尝试条件：任何表面误差实验必须同时输出 `e=C_test-C_ref` 与 `abs(e)`，并在执行前验证位置标签和 reference role。

## F-Q1-005 BDF2 候选未通过完整网格安全门

对应实验：EXP-Q1-NUM-REMEDIATION

方法：在相同 M1 空间 FVM、Robin 边界和 Picard 设置下，比较“BE 首步+BDF2”与 BE，测试 `N=320`、`dt=1/0.5/0.25 s`，并检查完整网格和论文点。

现象：BDF2 的论文点在 `dt=0.5→0.25 s` 下温度和含水率均为 `0/35` 个四位小数差异；但完整网格含水率 L∞ 差为 `0.0011151331 kg/kg`，Richardson 剩余估计为 `0.0006163227 kg/kg`，全网格安全裕量不足。

失败原因：早期时间、表面附近的含水率时间误差仍占主导；该候选不能仅凭论文点稳定就升级为最终配置。

已尝试修复：保留 BE 参考，加入独立基准、误差定位、逐区域 Richardson 和四舍五入阈值距离分析；未放宽门槛，未生成工作簿。

最终判断：BDF2 是有证据支持的数值候选，但当前 Q1 Result & Deliverable Gate 仍 `BLOCKED`。

是否放弃：否。

重新尝试条件：人工决定是否进行针对早期/表面误差的最小诊断；不得直接生成 `result1.xlsx`。
