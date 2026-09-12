# CUMCM 数学建模项目 Agent 工作规范

本文件是项目级 Agent 规范。目标是让工作在多轮会话、上下文压缩和不同 Agent 之间保持可恢复、可追踪、可复现、可审计。

## 1. 启动协议：先恢复上下文，再修改

每次开始新任务或恢复项目时，禁止立即修改代码或文档。按以下顺序检查：

1. `AGENTS.md`
2. `docs/PROBLEM_SPEC.md`
3. `docs/STATE.md`
4. `docs/TODO.md`
5. `docs/DATA_CATALOG.md`
6. `docs/DECISIONS.md` 中最近且与当前任务相关的决策
7. `docs/EXPERIMENTS.md` 中相关实验
8. `docs/FAILURES.md` 中相关失败
9. `docs/FINDINGS.md`
10. `docs/ASSUMPTIONS.md`
11. `docs/HYPOTHESES.md`
12. `docs/VALIDATION.md`
13. `docs/CLAIMS.md`
14. `docs/RUNBOOK.md`
15. `docs/SOURCES.md`
16. `docs/HANDOFF.md`
17. `git status` 与最近的重要 commit；若当前目录不是 Git 仓库，明确记录这一事实，不自行假设存在版本历史
18. 当前任务涉及的代码、数据、实验结果和论文部分

完成检查后，先输出简短的 `Current Project Status`，至少包括：当前问题、已完成内容、主模型/主方案、Baseline、最好实验、已知失败、阻塞项、最高优先级任务和推荐下一步。

## 2. 证据纪律

- `HYPOTHESES.md` 中的内容是待验证想法，不得写成事实。
- `FINDINGS.md` 只记录有数据或实验支持的发现。
- `DECISIONS.md` 记录影响后续工作的选择及其理由。
- `CLAIMS.md` 记录论文主张及可核验来源。
- 论文中的重要数字必须来自真实数据、程序输出、明确计算或可靠来源；无法验证时标记 `UNVERIFIED`，绝不补写或猜测。
- 每个重要实验必须有唯一 `EXP-xxx` 编号，并尽量保存配置、指标、说明和代码/数据版本。

## 3. 实验与数据规范

- 复杂模型应与简单 Baseline 比较，并说明性能、复杂度、可解释性和过拟合风险。
- 新模型、特征工程、参数搜索、数据处理变化和新评价指标属于需要记录的实验活动，完成后同步更新相关文档。
- `data/raw/` 只读：不修改、不覆盖、不删除。清洗和转换结果写入 `data/interim/` 或 `data/processed/`，并通过脚本尽量复现。
- 实验详细产物放在 `experiments/EXP-xxx/`；`docs/EXPERIMENTS.md` 只保存索引和关键结果，避免日志膨胀。
- 必须检查数据泄漏、划分方式、交叉验证、残差、异常值、敏感性、鲁棒性、稳定性、边界情况、Baseline 和现实一致性。

## 3.1 Official Source Protection

`A题/` 是官方题目与附件的 `OFFICIAL_SOURCE / IMMUTABLE_SOURCE` 区域。

- 不得修改、覆盖、删除、重命名或直接写入 `A题/` 中的任何文件。
- `A题/附件/附件3/result1.xlsx` 至 `result4.xlsx` 是官方结果模板，也是原始资产。
- 任何生成结果必须从官方模板复制到 `deliverables/candidate/` 后写入，经过结构验证、数值验证、格式验证和人工确认后，才可进入 `deliverables/final/`。
- 不得把同一批官方二进制文件机械复制到 `problem/` 或 `data/raw/`，避免出现多个“原文件”来源。`problem/README.md` 和 `docs/DATA_CATALOG.md` 负责索引实际位置。

## 3.2 单位与精度

所有后续程序必须显式记录原始单位、内部计算单位和输出单位。禁止隐式单位转换。至少支持并明确标记：`s`、`h`、`cm`、`m`、`°C`、`K`、`kg/kg`、`kg/m^3`、`J/(kg·K)`、`W/(m·K)`、`W/(m²·K)`、`m/s`、`m²/s`。

内部计算保持完整精度。只有生成最终官方输出文件时，才按题面要求统一四舍五入。

## 4. 操作权限

### Level 1：可自主执行

阅读、数据分析、新建实验、编写测试、修复普通 Bug、绘图、小规模重构和补充文档。

### Level 2：可执行但必须记录

新模型实验、特征工程、参数搜索、数据处理策略变化和新增评价指标。必须更新 `EXPERIMENTS` / `DECISIONS` / `FINDINGS` 中适用的记录。

### Level 3：先请求人工确认

更换最终主模型、改变核心问题定义或关键数学假设、删除重要实验或原始数据、改变最终评价指标、推翻重要已确认决策、大规模重构，以及修改论文核心结论。

## 5. Git 规范

若项目使用 Git，提交信息可使用：`data:`、`exp:`、`model:`、`fix:`、`paper:`、`docs:`、`refactor:`。重大节点可建议创建 `q1-final`、`model-freeze`、`submission-candidate` 等 tag。

禁止危险 Git 操作（如强制重置、覆盖式回退或删除历史），除非用户明确授权。

## 6. Freeze Mode

进入 `FREEZE MODE` 后，默认不更换主模型、不引入全新复杂模型、不大规模改动数据流程或重构代码。优先进行 Bug 修复、验证、敏感性分析、图表、论文、引用、排版、附录和可复现性检查。发现致命问题时先说明风险并请求人工确认。

## 7. Session Close Workflow

用户要求结束本轮、保存进度、更新记录或准备交接时，按以下顺序执行：

1. 检查 `git diff/status`；
2. 检查本轮新增或修改的实验；
3. 更新 `EXPERIMENTS`、`FAILURES`、`FINDINGS`、`DECISIONS`、`ASSUMPTIONS`、`HYPOTHESES`、`VALIDATION`、`CLAIMS`；
4. 更新 `TODO`；
5. 最后更新 `STATE`；
6. 更新 `HANDOFF`；
7. 检查文档、代码、结果和论文的一致性；
8. 输出简短 Session Summary。

`STATE.md` 只表示当前真实状态，不积累历史；`HANDOFF.md` 只保留下一位 Agent 立即需要的信息。

## 7.1 Mandatory GitHub Sync After Task Completion

自 2026-09-12 起，经人工批准，任务完成的 Git 闭环必须包含 GitHub 同步。该规则适用于本仓库后续所有任务，详见 `docs/GITHUB_SYNC_POLICY.md`：

1. 完成工作后先执行与任务相关的验证、受保护路径检查、敏感信息扫描和 staged diff 检查。
2. 将所有应纳入版本控制的项目文件和本轮提交纳入普通 Git commit；需要追踪的 Git LFS 对象必须保持可上传状态。
3. commit 后执行 `git fetch origin`，检查 `origin/main...HEAD` 的 ahead/behind。若远端领先或发生 divergence，停止同步并报告，不覆盖远端历史。
4. 无冲突时执行普通 `git push origin main`；禁止 force push、reset、rebase、覆盖式回退和历史改写。
5. 执行 `git lfs push --all origin main`、`git lfs fsck`，并用 `git push origin --tags` 同步正式标签。
6. 最后用本地 `HEAD` 与 `git ls-remote origin refs/heads/main` 做 SHA 精确比较，确认工作树 clean，并报告同步结果。

`LOCAL COMMIT ONLY`、`DO NOT PUSH` 以及“因为仓库为 Public 所以不推送”不再是未来任务策略，均已被本次人工批准的永久同步政策取代。历史审计记录中的原始表述不得改写；若普通 push 或 LFS 同步失败，任务必须明确标记为 GitHub sync failed，不得宣称闭环完成。

## 8. 文件地图

- 当前状态：`docs/STATE.md`
- 任务队列：`docs/TODO.md`
- 建模决策：`docs/DECISIONS.md`
- 实验索引：`docs/EXPERIMENTS.md`
- 失败记录：`docs/FAILURES.md`
- 已验证发现：`docs/FINDINGS.md`
- 待验证假设：`docs/HYPOTHESES.md`
- 数学假设：`docs/ASSUMPTIONS.md`
- 验证清单：`docs/VALIDATION.md`
- 论文证据账本：`docs/CLAIMS.md`
- 会话交接：`docs/HANDOFF.md`
- 题目事实登记：`docs/PROBLEM_SPEC.md`
- 官方资产目录：`docs/DATA_CATALOG.md`
- 可复现运行手册：`docs/RUNBOOK.md`
- 文献与来源登记：`docs/SOURCES.md`
- 交付隔离区：`deliverables/candidate/`、`deliverables/final/`
