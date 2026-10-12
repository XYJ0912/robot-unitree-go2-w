# Go2W 接入记录索引

截至 2026-10-12，本目录归档开发笔记本上的 Go2W 只读接入记录。本次同步仅涉及文档；目标仓库仍以 Go2 部署代码为基线，独立 Go2W commissioning 原型留在本地交接目录，尚未作为可复现功能提交到此仓库。归档文档按形成时间保留原话，状态变化以本页和较新的审计为准。

## 已真机验证（只读）

- 专用有线网卡 `enp131s0=192.168.123.99/24` 连通 Go2W 网络；`192.168.123.18` 是拓展坞 SSH 端点。未改变机载环境。
- 笔记本安装于工作区的官方 Unitree SDK2，经 DDS 接收 `rt/lowstate` LowState 与 `rt/lf/sportmodestate` SportModeState；低层 tick 递增。首次短采集 high=3、low=143；后续 10 秒采集 high=100、low=4998。
- 同次 10 秒采集中，候选 `rt/utlidar/cloud` 收到 0 帧；实际 LiDAR topic、QoS 和发布状态尚未确认。
- 独立本地原型的一次 `VideoClient::GetImageSample` 只读取图返回 JPEG；本机 camera snapshot 原型在 Atlas 注册为 ACTIVE，经回环 MCP 实际调用得到 `1920×1080 rgb8` 单帧。这只证明该实验链路，不代表本仓库已有可部署相机能力；图像设备时间和 optical frame 未确认。

## 继承自 Go2 官方仓库，尚未在 Go2W 验证

根目录及现有 `docs/`、`packages/`、`deploy/` 中的 Go2 manifest/Soma、底盘和传感器适配、URDF/TF、导航、语音、运动控制及 Go2 现场验收都属于 Go2 参考实现。Go2W 的轮腿运动语义、机体几何、传感器来源、坐标系、时间戳和安全停止效果不能据此推定。原有 Go2 安全 gate 也不构成 Go2W 运动许可。

## 当前待验证 / WIP

- 本仓库中的独立 Go2W deployment 与真实状态 provider 尚未提交。历史 mock health 注册不等于真机 health 接入。
- 完整 IMU 单位/frame、odometry 原点与坐标系、TF、LiDAR topic/QoS/点云字段、相机持续流/标定/源时间均待验证。SportModeState 的设备 stamp 曾为零，不能直接用于新鲜度验收。
- 本地相机原型曾注册 Atlas，但可复现的本仓库构建/启动/Atlas 接入尚未完成；Pilot/Executor 对真机能力的调用未验证。
- 任何 Go2W 运动、StopMove/急停效果、导航均未测试且未获本记录授权。保持 `GO2_ALLOW_MOTION=false` 或等价关闭态。

## 过程资料

- [Go2W 审计与后续相机增量](records/GO2W_AUDIT_20261012.md)：目前最完整的阶段记录，含证据等级、Go2/Go2W 差异及本地 commissioning 结果。
- [首次 SDK2/DDS 只读接收输出](records/GO2W_DDS_READONLY.md)：保留实际状态样本与计数。
- [只读 DDS probe 说明](records/GO2W_DDS_PROBE_README.md)：原交接包的构建与订阅边界；命令仅适用于原交接目录。
- [早期接入报告](records/INTEGRATION_REPORT.md)：形成于相机原型和 Atlas 验证之前，文中的“未接入”是当时状态。
- [本地 Go2W 原型说明](records/LOCAL_GO2W_PROTOTYPE_README.md)：保留 commissioning 构建、启动和安全限制；涉及的功能代码不在本仓库。
- [原交接结果](records/CURRENT_RESULTS.md)及[本机准备说明](records/LOCAL_PREPARATION.md)：交接快照，部分“未安装/未连接”表述已被后续进展取代；其中相对路径指原交接包，未随本仓库迁入。
- [本地 commissioning 日志摘录与保留位置](records/COMMISSIONING_LOG_NOTES_20261012.md)：保留可核对的关键事件；按仓库规则未提交原始运行日志。

原始日志、构建输出和未提交的 Go2W 原型仍在交接工作区，不在本仓库。此处未归档凭据、图像、点云或私人设备配置。
