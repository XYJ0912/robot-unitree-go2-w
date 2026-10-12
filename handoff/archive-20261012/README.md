# GO2-W 接入交接包 · README

## 解压后立刻开始

把整个 `GO2W_HANDOFF` 文件夹设为 Agent 工作目录，并发送：

> 请读取当前目录的 `README.md` 和 `START_AGENT_PROMPT.md`，按提示词开始 GO2-W 接入。先检查现有连接和环境，有权限就推进只读状态接入；没有真机连接也先完成源码与 mock 准备。可查信息自行核实，不要求我重述旧对话。

相关入口：[接入提示词](START_AGENT_PROMPT.md) · [当前成果](CURRENT_RESULTS.md) · [版本](SOURCE_VERSION.json) · [回报模板](INTEGRATION_RESULT_TEMPLATE.md) · [本地验收说明](reports/MAIN_DEPLOYMENT_ACCEPTANCE.md)

本包用于把 Robonix 软件栈交接给负责 GO2-W 接入的同学。包内是**固定源码快照 + 已应用的本地 Executor 生命周期补丁 + 本地模拟部署与两轮主入口验收材料**，用于让接收方在无真机、无原机环境的情况下先完成软件侧准备。所有文档内链接均为相对路径，解压根记为 `<BUNDLE_ROOT>`；文档不会也**不应**使用原持有人电脑 WSL 路径，那不是你的路径。

## 一、包内内容

- `source/robonix/`：主源码固定快照。
- 四个固定子模块内容：随包提供、版本固定。
- `patches/executor-lifecycle.patch`：本地 Executor 生命周期补丁，**已在 source/robonix 内应用**，接收方不要重复 `git apply`。
- 五个改动源码文件（见补丁与 SOURCE_VERSION.json 记录）。
- `source/robonix/SOURCE_VERSION.json`：主源码基点 `62057c696cb49f01f14d9a4f16c9685e59b9e79b`，加本地生命周期补丁；原提交可在公开仓库 <https://github.com/syswonder/robonix> 核对。Git 元数据不随包发送，版本以该文件为准。
- `reports/`：本地模拟部署结果说明。
- `evidence/`：两轮主入口验收的去本机路径摘要。
- 源码 LICENSE 及第三方许可证均已保留，请继续遵守。

## 二、包内**没有**什么

没有预编译二进制、没有真实凭据/密码、没有机载模型、没有已验证的 GO2-W 硬件适配。因此本包不代表机器人已经接入，也不含可直接执行的旧电脑回滚命令（旧可用版本与历史证据留在原电脑）。包内同时未含 `.codegraph`，无需建立索引；若你的现有接入仓库里已有 `.codegraph`，优先走 CodeGraph，但不要自动重建。

## 三、环境与运行前提

- Python 3.10+。原环境曾使用 Rust 1.99.0，仅供参考，**不要照抄其他电脑的缓存或工具链名称**。
- 接收方必须自行阅读 Cargo 配置与仓库规则，检查本机工具链后决定版本。
- `scripts/collect_host_info.sh` 是只读检查：仅采集**当前运行机器**的型号/CPU/内存/系统/工具版本，不登录机器人、不发送运动指令。在开发电脑上运行只代表开发电脑，不代表 GO2-W。

## 四、建议阅读顺序

1. 本 README 与 `CURRENT_RESULTS.md`
2. `SOURCE_VERSION.json`
3. `source/robonix/AGENTS.md` 规则
4. `START_AGENT_PROMPT.md`（交给接入 Agent 的起始指令）
5. `INTEGRATION_RESULT_TEMPLATE.md`（交付时填写）

## 五、范围边界（务必先读）

真实模型自主规划、GO2-W 硬件、物理运动/感知/导航均**未验证**。规划环节为 fake VLM 预置，speech 只是 mock 回执。原机器已停止服务，不代表你的机器上无服务。先做软件适配，暂无硬件改造依据；不要先下载全套导航仿真/模型，不换固件，不用 Go2 型号替代 Go2-W。Unitree 官方 SDK 与 GO2-W 资料仅用于核对，不是本包已安装/验收的软件；SDK 例程可能触发运动或控制权切换，必须先读代码，不直接运行未知运动例程。
