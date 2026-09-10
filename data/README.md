# Data Layout

- `raw/`：原始数据，只读，不修改、不覆盖、不删除。
- `interim/`：中间处理结果。
- `processed/`：可供建模使用的处理后数据。

当前官方原始题目与附件实际位于 `A题/`，被定义为 `OFFICIAL_SOURCE / IMMUTABLE_SOURCE`。本项目不把它们复制到 `data/raw/`，以避免出现第二个原始数据源。

所有重要数据转换应通过 `scripts/` 中的脚本完成，并记录输入、输出和版本信息。
