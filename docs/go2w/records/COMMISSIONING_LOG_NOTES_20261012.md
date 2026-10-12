# 本地 commissioning 日志摘录（2026-10-12）

记录来源：交接目录中的 `source/robot-unitree-go2w/rbnx-boot/logs/`。这是历史本地实验日志的人工摘录，不是本仓库当前代码的运行结果。仓库 `CONTRIBUTING.md` 禁止提交原始 logs，因此原始日志仍保留在交接目录；本次未删除或修改。

- 18:23:03 本地 `robonix-go2w-readonly-commissioning` 开始 boot；18:23:10 报告 all components up；18:23:41 收到停止信号并关闭子进程。
- camera snapshot 日志显示注册 `go2w_camera_snapshot`，能力为 `robonix/primitive/camera/snapshot` 和 lifecycle；Atlas 端点、lifecycle gRPC 与 MCP HTTP 均绑定 `127.0.0.1`。Driver 状态经历 REGISTERED → INACTIVE → ACTIVE，随后收到一次 MCP CallToolRequest，并在停止时到 TERMINATED。
- mock health 日志显示 `go2w_health_mock` 注册、health/state 与 health/stream 连线，Driver 到 ACTIVE 后正常终止。它仍是 mock，不能作为真实 Go2W health 证据。
- 单独的 SDK2/DDS 采集计数与样本见 [GO2W_DDS_READONLY.md](GO2W_DDS_READONLY.md) 和 [GO2W_AUDIT_20261012.md](GO2W_AUDIT_20261012.md)；这些采集与 mock health 不是同一条状态桥接链。

原日志包含会话标识和机器本地路径；本摘录未搬运这些字段，也未包含凭据。相机像素数据未保存。
