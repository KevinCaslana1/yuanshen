# CUMCM 数学建模项目 Agent 工作规范

本文件是项目级 Agent 规范。目标是让工作在多轮会话、上下文压缩和不同 Agent 之间保持可恢复、可追踪、可复现、可审计。

## 1. 启动协议：先恢复上下文，再修改

每次开始新任务或恢复项目时，禁止立即修改代码或文档。按以下顺序检查：

1. `AGENTS.md`
2. `docs/STATE.md`
3. `docs/TODO.md`
4. `docs/DECISIONS.md` 中最近且与当前任务相关的决策
5. `docs/EXPERIMENTS.md` 中相关实验
6. `docs/FAILURES.md` 中相关失败
7. `docs/FINDINGS.md`
8. `docs/ASSUMPTIONS.md`
9. 必要时检查 `docs/VALIDATION.md` 和 `docs/CLAIMS.md`
10. `git status` 与最近的重要 commit；若当前目录不是 Git 仓库，明确记录这一事实，不自行假设存在版本历史
11. 当前任务涉及的代码、数据、实验结果和论文部分

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

