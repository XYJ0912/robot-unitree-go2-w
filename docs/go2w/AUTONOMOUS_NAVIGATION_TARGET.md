# Go2W 自主导航目标与验收边界

状态：2026-10-12 核对本仓库 `main` 的 Go2W commissioning 清单、继承的 Go2 架构/安全文档和本机真机只读记录。本页定义未来完成标准，不表示已获运动授权或已完成验收。历史记录保留原形成时状态；当前状态以本页和 [索引](README.md) 为准。

## 完成标准

操作者通过 Robonix Pilot 提交一个**当前地图中已验证、可到达**的目标；系统经 Atlas/Executor 的能力链调用 Robonix navigation service，再由 Nav2 在 Go2W 的实时定位、TF 和障碍代价地图上规划与控制。只有受保护、唯一的 Go2W 底盘适配器可以把速度命令送到 Unitree SDK2。Pilot 能收到进行中、成功、失败或取消的真实反馈；机器人在目标容差内停止，取消、失联、状态/定位/测距失效及故障时也能安全停止。至少完成一次现场监督的目标到达、取消/停止和返程或第二目标验证，留下同一会话的任务、传感器、地图、控制与停止证据。

```text
Pilot 的已验证目标
  → Robonix 能力/导航服务（Atlas + Executor）
  → Nav2 目标动作、规划、定位与实时障碍代价地图
  → 唯一受保护的速度通道
  → Go2W 专用底盘适配 / SDK2
  → Go2W 实际运动与停止
  → 状态、定位和任务反馈回到 Pilot
```

“SDK2 能发 Move”、“底盘短距离能动”、“Nav2 在 Go2 上通过”及“Pilot 离线 fixture 成功”都**不单独构成**上述验收。第一版可以使用预先测量的地图与地标，不要求视觉发现未知目标；单帧 camera snapshot 也不是已验证的导航输入。实际导航传感器组合必须在这台 Go2W 上测量后确定。

## 当前证据与缺口

| 层 | 已确认 | Go2W 完成前还需证明 |
|---|---|---|
| 网络和 SDK2 状态 | [真机确认] 笔记本 `enp131s0` 的 DDS 收到 LowState 与 `rt/lf/sportmodestate`；[真机确认] 相机一次取图与旧位置本地 snapshot→Atlas 调用成功 | 迁入本仓库后复现构建/启动；持续状态、失效与时间基准；真正的状态 provider |
| 定位和地图 | [代码确认] 继承的 Go2 实现有 odom、TF、RTAB-Map/Nav2 与地图生命周期门 | [尚未确认] Go2W 的 odom 坐标/漂移、IMU、`map→odom→base_link` 唯一发布者、实测机体尺寸/外参、可加载地图和定位质量 |
| 障碍感知 | [真机确认] 候选 `rt/utlidar/cloud` 在一次 10 秒订阅为 0 帧，同时状态流正常 | [尚未确认] 真实 LiDAR 或其他经验证测距源、topic/QoS、点云时间/坐标、障碍标记与清除、丢失后禁止继续行驶 |
| Robonix 到 Nav2 | [代码确认] Go2 参考仓库有 Pilot 语义目标、导航服务、Nav2 与反馈链 | [尚未确认] Go2W 清单内的对应服务、Atlas/Executor/Pilot 实际调用、目标与地图版本校验、反馈/取消/失败传播 |
| 底盘和停止 | [官方 SDK2 源码确认] Go2W 示例使用 `go2::SportClient::Move/StopMove`；[代码确认] 本仓库 Go2 底盘有独立进程与多重安全门 | [尚未确认] 此 Go2W 的轮腿模式、速度语义、单一控制权、真实 StopMove/官方急停效果、失联 watchdog、限速与安全距离；不得直接套用 Go2 配置 |
| 现场自主导航 | 无 Go2W 运动或导航实测 | [尚未确认] 监督下最小动作、目标到达、取消/停止、障碍/传感器故障响应及返程/第二目标 |

高层 SportModeState 的**设备时间戳实测为零**。继承 Go2 的运动门要求源时间非零且严格递增；目前不能直接解锁。必须先核实时间来源，或设计并独立验证不弱于原门的新鲜度/连续性机制；不能仅以笔记本接收时间掩盖重复、滞留或重放状态。现有 health 原语是 mock，`charging` 等未知字段也不能猜值填入真实合同。

## 分阶段关口

1. **可复现的软件基线（无运动）**：固定经核对的 Go2W SDK2/ROS 依赖，移除对交接目录的运行时依赖；在新路径完成 `rbnx validate/build/boot`、camera 与 Atlas 注册复核。当前 Go2W profile 仅有 camera snapshot 与 mock health，不能用继承 Go2 的启动结果代替。
2. **真机只读导航输入**：建立真实状态、IMU、odom/TF 和可用测距数据；测量 QoS、时间、frame、footprint 与外参，保存只读证据。不要求修改共享机器人机载环境；默认所有 Robonix、适配器和 Nav2 进程都在开发笔记本。
3. **静止定位与隔离回放**：在确认的地图上验证唯一 `map→odom→base_link`、定位漂移、两层代价地图障碍标记/清除及传感器失效；隔离 ROS 域中测试目标、取消、反馈和速度归零，命令只能到无执行能力的 sink，不连真机控制接口。
4. **Go2W 专用运动安全实现（仍禁用）**：核对 Move/StopMove 与轮腿模式；实现独占命令源、模式/状态/定位/传感器新鲜度门、限速、watchdog、故障锁定和明确的控制权交接。完成离线故障注入；默认 `GO2_ALLOW_MOTION=false`。
5. **现场监督的分级运动验收**：先书面列出官方急停、StopMove、场地、动作上限及可能实际动作，并取得用户针对该次测试的明确批准；随后才可做最小运动/停止，再做 Pilot→Nav2→Go2W 的短目标、取消、障碍与失效、返程/第二目标测试。每个失败都应保持禁动，不能把上一轮批准自动沿用。

任何运动测试之前停在第 4 关。对共享 Go2W 不修改系统环境、网络配置、systemd 或固件；若最小机载组件被证明必需，另行报告并取得明确批准。

## 参考边界

- [Go2W 真机审计](records/GO2W_AUDIT_20261012.md)与 [DDS 输出](records/GO2W_DDS_READONLY.md)是本机只读证据；相机验证只覆盖一次 snapshot。
- [当前 Go2W commissioning 清单](../../deploy/go2w-readonly-commissioning/robonix_manifest.yaml)没有导航服务、Nav2、Go2W chassis 或真实状态 provider。
- [Go2 架构](../ARCHITECTURE.md)、[Go2 验收矩阵](../ACCEPTANCE.md)、[Go2 安全门](../SAFETY.md)可作结构参考，但其中的硬件参数、Go2 现场 PASS 和运动许可不适用于 Go2W。
- [官方 SDK2 Go2W 示例（固定提交 `63096d0`）](https://github.com/unitreerobotics/unitree_sdk2/blob/63096d0ac0c5d2dec9d6e0c22cd5233410ca2f36/example/go2w/go2w_sport_client.cpp)中的 `Move`、`StopMove` 调用是**源码确认**，不是此共享机器人上的停止效果或 1 秒自动停机真机确认；不得运行含姿态/运动调用的示例来“探测”。
