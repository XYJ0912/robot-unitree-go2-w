# 本机准备：从解压目录开始

本包以相对路径组织，源码已经包含 Executor 生命周期修复和四个固定子模块的文件。没有 `.git`、构建缓存、原环境虚拟环境或可直接给机载模块使用的二进制。接入 Agent 可直接读源码和做离线适配；构建依赖按接收方已有权限恢复。

## 1. 检查包和当前机器

在解压出的 `GO2W_HANDOFF` 根目录运行（Python 3.10+）：

```text
python scripts/check_bundle.py
```

Linux/WSL 的只读环境检查：

```bash
bash scripts/collect_host_info.sh
```

Windows可用：

```powershell
powershell -NoProfile -File .\scripts\collect_host_info.ps1
```

它们不执行 SSH、SDK、DDS 或运动命令，不修改系统配置。结果只描述运行脚本的这台机器；如要确认机载模块，请在已经登录且已授权的机载终端运行Linux脚本，不把WSL结果当机载资源。

## 2. 本地源码与依赖

先读 [仓库规则](source/robonix/AGENTS.md)、[Cargo配置](source/robonix/Cargo.toml)、[SDK说明](source/robonix/pylib/robonix-api/README.md)、[开发文档](source/robonix/docs/docs/developer-guide.md)。基点及子模块版本见 [SOURCE_VERSION.json](SOURCE_VERSION.json)。

原已验收环境为Linux x86_64、Python3.10、Rust1.99.0。这是历史环境，不意味着接收方已有同样依赖，也不证明ARM机载兼容。编译时使用当前机器的架构与工具链；不要复制原电脑缓存或在机载模块运行x86_64可执行文件。部分源内脚本依赖Git元数据，执行前先审阅并适配本包的源码快照形式；不要直接做submodule update或升级上游来覆盖补丁。

先构建六个已验证核心组件（在 `source/robonix` 下）：

```bash
cargo build --locked -p robonix-atlas -p robonix-executor -p robonix-pilot -p robonix-liaison -p robonix-cli -p robonix-codegen
```

若缓存齐全可加 `--offline`；缺缓存时按现场网络许可恢复正常构建依赖，不改Cargo.lock。本包不要求先装ROS2/Webots/Docker。SDK常规依赖使用项目虚拟环境，安装本包的 `pylib/robonix-api`，不要装到另一份旧源码上。按仓库代码生成入口生成能力与Atlas控制面的接口，再选择最小mock闭环；本包没有携带原机器的私有env.sh或生成缓存，Agent须根据本机路径组织它们。

## 3. 如何进入GO2-W接入

- 真机未连接：从源码现有的 Primitive/Service、Atlas注册及Soma/传感器合同准备只读状态桥接和mock输入。产出接口矩阵与可运行的本地适配，不假称实机已成功。
- 真机已连接且有只读访问：核实SDK/固件、网卡与实际topic/消息/时间/单位/坐标系，先订阅状态，验证同一数据能出现在Robonix注册能力中。逐项记录来源与失效标志。
- 运动阶段：先交付受控动作/停止方案，由现场用户授权后执行。官方例程可能发送运动或切换控制权，不能以“查看例程”为由直接运行。

独立 [Go2部署包](https://github.com/syswonder/robot-unitree-go2) 与 [官方SDK](https://github.com/unitreerobotics/unitree_sdk2) 仅作接入参考，没有随本包克隆/安装，GO2-W兼容需核对。先用现有能力接口，避免一开始引入完整导航栈或硬件改造。

本包没有可执行的旧电脑回滚入口。接收方发生实现/部署修改时，自行备份当前本机可用状态、保存版本对应的新日志，只关闭自己启动的进程；不要停掉厂商或同学已有服务。
