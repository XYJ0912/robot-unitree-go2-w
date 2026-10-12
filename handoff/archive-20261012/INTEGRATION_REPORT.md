# GO2-W 接入报告

> 本报告仅记录本轮可核对的只读证据。已通过 SSH 登录拓展坞，并在笔记本使用 SDK2 订阅 GO2-W DDS 状态；未执行任何运动、站立、模式切换或控制权操作。

## 1. 环境

| 项 | 值 |
| --- | --- |
| 日期 / 执行人 | 2026-10-12 / Codex 接入会话 |
| 接收方 OS 与版本 | Ubuntu 26.04.1 LTS，Linux 7.0.0-38-generic，x86_64 |
| 解压根 `<BUNDLE_ROOT>` | `/home/xiongyingjie/Projects/GO2W_HANDOFF_20261012/GO2W_HANDOFF` |
| 本机 CPU / 内存 | YAOSHI Series；30 GiB 内存（脚本采样时约 22 GiB available） |
| Python 版本 | 系统 Python 3.14.4；mock 隔离环境 Python 3.12.15 |
| Rust / 工具链版本（含来源） | rustc 1.99.0、cargo 1.99.0（本机 PATH） |
| 是否运行 `scripts/collect_host_info.sh` | 是；只代表当前开发主机 |
| 包完整性 | `scripts/check_bundle.py` 通过；快照无 Git 元数据，生命周期补丁在源码中 |

## 2. 机器人侧

| 项 | 值 |
| --- | --- |
| 设备身份确认方式 | 更新后的现场指引指定拓展坞 SSH 目标为 `192.168.123.18`。本机 `192.168.123.99/24` 经 enp131s0 到该地址三次 ICMP 连通，0% 丢包、平均 0.176 ms；ARP 邻居处于 REACHABLE |
| 模块型号 | GO2-W（现场确认）；拓展坞硬件报告为 NVIDIA Orin NX Developer Kit |
| 机载终端是否可进入 | 是。重试后 `.18` 的 SSH 服务返回 `OpenSSH_8.2p1 Ubuntu-4ubuntu0.5`，`unitree` 登录成功；此前横幅超时已恢复 |
| SDK / 固件版本 | GO2-W 固件未确认；拓展坞限定路径内未找到 Unitree SDK 或 Robonix 安装。笔记本安装官方 SDK2 源码提交 `63096d0ac0c5d2dec9d6e0c22cd5233410ca2f36`（CMake 版本 2.0.0） |
| 已确认 IP（是否只读授权） | `192.168.123.18`；SSH 只读命令已执行成功，拓展坞 eth0 同为 `192.168.123.18/24` |
| 既有服务清单 | Ubuntu 20.04.5 LTS、aarch64、Python 3.8.10；安装 ROS Foxy 和 Noetic；`ssh.service` 与 `unitree-upgrade.service` 正在运行。进程清单未见机器人 ROS 节点，`docker ps` 无运行容器。Foxy 的只读 `topic/node list --no-daemon` 返回 `std::bad_alloc`；Noetic 的 `rostopic` 缺 Python 模块。此前对 `.161` 的 HTTP/SSH 检查不是本轮指定目标 |
| 未确认项 | 机器人固件、DDS QoS、坐标系、更多传感器真值；拓展坞 UTC 系统时间仍在 `1970-01-01`，NTP 已启用但未同步；收到的高层状态设备时间戳为零 |

## 3. 接口矩阵

| 能力 | SDK 入口 | 消息与单位 | 坐标系 | 实机只读可用 | 未验证 |
| --- | --- | --- | --- | --- | --- |
| 设备状态 | SDK2 `ChannelSubscriber<SportModeState_>`，`rt/lf/sportmodestate` | mode、error_code、position、IMU yaw；设备 stamp 为 0 | 位置/IMU frame 未确认 | 是，仅 SDK2 直读；Robonix 未桥接 | 字段单位/坐标系、设备时间基准 |
| 电池 / 电源 | SDK2 `ChannelSubscriber<LowState_>`，`rt/lowstate` | power_v≈29.7653 V、power_a≈1.1 A、BMS SoC=63% | 不适用 | 是，仅 SDK2 直读；Robonix 未桥接 | 充电/剩余时间、与机身显示对照 |
| 关节 / 姿态 | 未接入 | 无已声明能力 | 未确认 | 否 | 消息、关节名、单位、坐标系 |
| IMU | 已在高层状态中收到 yaw；尚未单独接入 | 可复用 `robonix/primitive/imu/imu`；加速度 m/s²、角速度 rad/s | 机身坐标系未确认 | 部分，仅 SDK2 直读 | 完整 IMU 数值、QoS、时间与机身坐标系 |
| 传感器（LiDAR/相机） | 未接入 | 可复用 lidar3d / camera rgb 标准 topic_out 合同 | 由实际 header.frame_id 确定 | 否 | 传感器型号、话题、标定、QoS、帧关系 |
| 网卡 / 接口 | 未接入 | 不适用 | 不适用 | 否 | 已授权 NIC、IP 与访问边界 |

## 4. 只读状态桥接

- 新增本地 mock：`source/robonix/examples/go2w_readonly/`，只声明 `robonix/primitive/health/state`、`robonix/primitive/health/stream` 与共享 Driver。
- 仅接受明确配置的本地 JSON 快照，唯一允许的运行时来源是 `source=mock`；配置 `read_only_real` 会在初始化阶段失败，避免把未核实数据标为实机。
- 每次读取均使用生产者时间 `observed_at_unix_ms` 计算 age / stale，并写入该软件包自己的 `rbnx-build/run/health-metadata.json`。标准 health 合同没有 provenance、timestamp 或 stale 字段，因此这些字段没有伪装成已有的 Atlas 合同字段。
- 本轮判定：`NOT_READY`（针对 Robonix 接入）。笔记本已收到实时 DDS 状态，但尚未注册到 Robonix；高层设备 stamp 为 0，桥接需使用笔记本接收时间和连续帧证据判断失效。

## 5. 源码改动与构建

- 基于 `SOURCE_VERSION.json` 的固定快照；已保留 Executor 生命周期补丁，未重复应用。
- 新增 `source/robonix/examples/go2w_readonly/`：清单、配置说明、离线快照验证、health provider、构建/启动/清理脚本、mock 样例和 3 项单元测试。
- 通过：`cargo build --locked -p robonix-atlas -p robonix-executor -p robonix-pilot -p robonix-liaison -p robonix-cli -p robonix-codegen`；快照缺 Git 元数据导致 CLI 构建显示版本默认值告警。
- 通过：`python3 -m unittest discover -s examples/go2w_readonly/tests -v`、`target/debug/rbnx validate examples/go2w_readonly`、隔离环境构建、生成 88 个 Python stub、运行时导入检查。
- 笔记本安装 `third_party/unitree_sdk2` 到工作区局部前缀（未改系统目录），以 `BUILD_EXAMPLES=OFF` 构建；新增 `tests/go2w_dds_probe/`，仅包含两个订阅端点。2026-10-12 16:44:31 CST 从 `enp131s0` 收到 3 帧 `rt/lf/sportmodestate` 与累计 143 帧 `rt/lowstate`：low tick 1050872→1050876，BMS SoC 63%，高层 mode 1/error_code 0；这证明 SDK2 DDS 状态接收路径可用。SDK2 对 GO2-W 高层话题的依据为官方 `example/go2w/go2w_sport_client.cpp`；本轮未运行该例程，因为它包含运动调用。
- 未运行 Robonix provider 进程或 Atlas；拓展坞根分区约 203 GiB 可用、内存约 13 GiB 可用；本机未见 cargo/rustc/uv，部署需要目标架构构建环境或隔离交叉构建。

## 6. 受控运动方案（待现场授权，未执行）

- 最小动作：无。先完成同一时刻的设备状态与现场真值比对，再另行提交动作方案。
- 前提条件：确认 GO2-W 身份、只读状态来源、急停/现场观察者、停止机制、时间/坐标/单位和书面动作范围。
- 明确范围与停止条件：仅在现场同学明确授权后制定；本轮未执行。
- 否决条件：无设备身份或只读真值、状态失效、坐标/单位不明、急停不可核对、任何未授权控制权切换。

## 7. 待确认问题

1. 核对拓展坞为何显示 1970 年以及机器人状态消息所用的时间基准；不修改时钟前先保存只读证据。
2. 核对 GO2-W 固件版本和机载状态发布者，与本机 SDK2 提交的兼容性。
3. 将已收到的状态桥接到 Robonix，确认字段单位、frame、QoS，并与现场显示核对 SoC/电压。

## 8. 结论

- [x] 本地软件适配和实机 DDS 直读已完成；拓展坞网络与 SSH 只读接入已确认
- [ ] 只读实机验证完成
- [ ] 受控运动已获授权并执行
- 本轮状态：`NOT_READY`（Robonix 注册未完成；SDK2 只读 DDS 接收通过）
- 已验证的具体能力与证据：本地 mock health 合同；官方 SDK2 在笔记本通过 `enp131s0` 接收 GO2-W 高层与低层状态，收到递增 tick 和电池/姿态数值。详情见 `reports/GO2W_DDS_READONLY.md`。
- 仍未验证的具体能力：Robonix 实机注册、固件、完整 IMU、相机、LiDAR、里程计坐标系、运动与急停。
- 归档日志路径与下位 Agent 下一步：mock 的本次生成产物在 `source/robonix/examples/go2w_readonly/rbnx-build/`（忽略目录）；获得现场只读连接后，以同一快照验证模型核对真值，再将经过核实的只读采集器接入，保持所有运动能力未声明。
