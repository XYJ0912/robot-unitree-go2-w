# GO2-W SDK2 只读 DDS 接收证据

- 日期：2026-10-12 16:44:31 CST（笔记本接收时间；UTC 08:44:31）。
- 路径：笔记本 `enp131s0`（`192.168.123.99/24`）→ GO2-W DDS；拓展坞 SSH 地址为 `192.168.123.18`。
- SDK：Unitree 官方 `unitree_sdk2`，提交 `63096d0ac0c5d2dec9d6e0c22cd5233410ca2f36`，工作区局部安装到 `third_party/unitree_sdk2/install/`。构建时 `BUILD_EXAMPLES=OFF`。
- 程序：`tests/go2w_dds_probe/main.cpp`，只建立 `ChannelSubscriber`，没有发布者、SportClient 或控制调用。订阅主题来自 SDK 的 GO2-W 示例 `example/go2w/go2w_sport_client.cpp`。
- 执行：`tests/go2w_dds_probe/build/go2w_dds_probe enp131s0`；退出码 0。

接收摘要：

```text
low topic=rt/lowstate count=1 received_unix_s=1791794671 tick=1050872 power_v=29.7653 power_a=1.128 bms_soc_percent=63
high topic=rt/lf/sportmodestate count=1 received_unix_s=1791794671 device_stamp=0.000000000 mode=1 error_code=0 position_m=0,0,0 yaw_rad=0.20487
low topic=rt/lowstate count=2 received_unix_s=1791794671 tick=1050874 power_v=29.7653 power_a=1.128 bms_soc_percent=63
low topic=rt/lowstate count=3 received_unix_s=1791794671 tick=1050876 power_v=29.7653 power_a=1.09382 bms_soc_percent=63
high topic=rt/lf/sportmodestate count=2 received_unix_s=1791794671 device_stamp=0.000000000 mode=1 error_code=0 position_m=0,0,0 yaw_rad=0.204987
high topic=rt/lf/sportmodestate count=3 received_unix_s=1791794671 device_stamp=0.000000000 mode=1 error_code=0 position_m=0,0,0 yaw_rad=0.204927
summary high=3 low=143
```

解释：两条状态流均收到多帧，低层 tick 递增，说明本机 SDK2 到 GO2-W 的只读 DDS 接收链路可用。高层消息 stamp 为零；设备时钟/坐标系未核对，因此不能把这些帧直接用于 Robonix 的时间新鲜度或里程计验收。下一步应使用本机接收时间和连续帧证据构建失效判断，并与机器人现场显示核对数值。
