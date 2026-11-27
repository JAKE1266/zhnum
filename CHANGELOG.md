# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式,
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.1] - 2026-11-27

### 修复
- 「万亿」按完整单位解析，修复 `10**12` 及以上整数往返失真。
- 金额改用 Decimal 四舍五入到分，修复 `2.675 → 2.67`；拒绝 NaN、Infinity 与非法输入。
- CLI 的 stdout/stderr 显式使用 UTF-8，修复 Windows 默认编码下中文输出崩溃。

### 变更
- 新增大数边界、金额精度、非有限值与旧编码 CLI 回归，共 29 项测试。
- 补齐 sdist 清单、真实 wheel 安装冒烟，以及 Ubuntu/Windows/macOS × Python 3.8/3.9/3.11/3.13 的 13 作业 CI。

## [0.1.0] - 2026-11-21

### 新增
- 核心功能实现(纯标准库,零第三方依赖)
- CLI 命令行入口
- 17 个单元测试
- GitHub Actions 三系统 × 多版本 CI
- 中文 README 与 MIT 许可证

### 变更
- 补齐徽章、项目结构与本日志,与其他仓库文档标准统一
