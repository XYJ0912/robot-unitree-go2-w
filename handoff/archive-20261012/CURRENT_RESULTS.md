# 当前结果（已完成 / 未验证）

## 一、真实已完成

- 六组件构建通过：Atlas / Executor / Pilot / Liaison / rbnx / Codegen。
- 真实注册、发现、执行、反馈链路可用。
- 主源码 + 主 Executor 二进制 + 实际主启动/停止入口已修复。
- 真实 Driver 状态迁移：INIT → INACTIVE / ACTIVATE → ACTIVE。
- 两轮主入口 Executor 均到 ACTIVE；Liaison → Pilot → Executor → mock_speech 动态文本回执并最终 done。
- CLI 直连 Pilot 的 write / read / list 三叶可用，当轮 24 字节独立读回成功。
- 执行中停用/关闭的排空与并发门控有效；真实 Driver 关闭进程、端口、heartbeat 正常；实际重启通过。
- 隔离阶段：`fmt`、`clippy` 通过；workspace 测试 358 通过、0 失败、2 个既有 ignored fixture。
- 主应用以原样生产补丁复用了上述测试，并新增主构建与现场模拟证据；**未再重跑 358 项**。

## 二、证据边界

- 规划为 fake VLM 预置；speech 仅为 mock 回执。
- 真实模型自主规划、GO2-W 硬件、物理运动/感知/导航**未验证**：不能说机器人已接入。
- 原机器上服务均已停止，但这不代表同学机器上没有服务。

## 三、GO2 接入现状

- 主仓库 README 引用独立仓库 <https://github.com/syswonder/robot-unitree-go2>，公开文档描述 Go2 高层 SportClient、ROS2/Nav2、传感器/底盘适配，尚不能证明 GO2-W 兼容。
- 官方 SDK 与 GO2-W 资料见 `START_AGENT_PROMPT.md` 第 7 节，仅供核对，不是本包已安装/验收的软件。
- 先做软件适配，暂无硬件改造依据。

## 四、研究成果说明（仅一段）

旧闭环共 12 任务 73 次调用，direct 0/4、thinking 4/4、hybrid 3/4，存在 16-token 截断且 hybrid 快路径为 0；新 114 请求的固定复核中，快模式 6/19、thinking 19/19 均格式有效，同文本规则 19/19，未训练 System1。四机制降为协议测试台，不构成论文创新，也不作为实机安全控制器。接入同学的重点是工程接入，不被要求重跑研究实验。

## 五、接收方仍需自行确认

当地工具链版本、模块型号、SDK 版本、机载终端可用性、既有服务清单与只读访问范围；以及是否已有 `.codegraph` 索引。

详见 [主部署结果说明](reports/MAIN_DEPLOYMENT_ACCEPTANCE.md)、[两轮原记录的可分享导出](evidence/main-acceptance.export.json) 与 [研究状态](reports/RESEARCH_STATUS.md)。这些是原环境证据，接收方验证须新建日志，不能把原PASS当作当前实机PASS。
