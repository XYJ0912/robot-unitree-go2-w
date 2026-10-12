# 已完成成果：本地模拟主部署修复

验收日期2026-10-12。版本为62057c69加本地Executor生命周期补丁；未提交、合并或推送上游。工程成果已应用原持有人主部署，不是只停留在隔离候选。源码快照见 [source/robonix](../source/robonix/)，补丁已应用，审查用diff见 [patches/executor-lifecycle.patch](../patches/executor-lifecycle.patch)。

## 修复行为

原Executor没有Driver却直接请求ACTIVE，Atlas拒绝它。修复复用真实共享 `robonix/lifecycle/driver`，服务可调用后INIT→INACTIVE、ACTIVATE→ACTIVE；启动失败明确退出。Execute门控默认关闭，任务在spawn前登记，重复活动ID拒绝；状态查询/取消/Driver保留可用。

DEACTIVATE/SHUTDOWN关闭接收，协调取消和任务/验证收尾，最终反馈入队后移除活动计划；同步能力自然返回，异步能力调用cancel。五秒排空、单次async cancel最多两秒、状态发布和server关闭时限是本补丁的生命周期策略。超时明确失败，门控保持关闭，不假报INACTIVE/TERMINATED；保留失败清理记录供重试。SHUTDOWN成功后实际停止server、heartbeat和进程。Atlas、能力合同、Driver IDL未改。

## 本地模拟验收

| 内容 | 保存结果 |
| --- | --- |
| 主源码/主Executor/实际主入口 | 完整补丁应用，从主源码locked构建，运行路径为实际主runtime |
| 两轮就绪 | 真实Driver发现/调用、Atlas ACTIVE、ListActivePlans业务可用 |
| Liaison任务 | 真实Liaison→Pilot→Executor→SDK mock_speech，一条成功叶、动态独立文本回执、最终done |
| CLI文件任务 | 直接Pilot→Executor write/read/list三条成功叶，各轮独立读回本轮workspace的24字节文件，最终done |
| 空计划负向 | 空in_progress被拒绝，零业务叶调用、无done；CLI退出0不等于任务成功 |
| 执行中停用与恢复 | 12次门控关闭后提交拒绝，已有能力释放与取消反馈收尾、INACTIVE后ACTIVATE并正常任务 |
| 执行中实际主stop | 另12次提交拒绝、排空收尾后Executor Driver关闭；无外部信号代替正常关闭 |
| 两轮关闭与重启 | 进程退出、端口关闭、TERMINATED、21秒heartbeat不刷新；实际第二轮重启任务/关闭通过 |
| 检查 | 隔离修复阶段fmt/clippy/workspace测试358 passed/0 failed/2已有ignored fixture；主应用原样补丁复用这些检查，并新增主构建与现场模拟证据，未再次跑358项 |

原环境服务最终停止，回滚备份和历史保留。接收方环境状态未知，不能把这份结果当成其机器人或当前进程的验收。

保存证据的可分享导出：[两轮主验收](../evidence/main-acceptance.export.json)、[执行中停用](../evidence/main-deactivate-drain.export.json)、[执行中关闭](../evidence/main-shutdown-drain.export.json)、[最终保存结果](../evidence/final-audit.export.json)。原电脑路径已替换为占位符，仅用来理解运行记录，不能照抄为接收方命令。

早期查询因代理超时、独立读回曾误用旧workspace，均修正后完整重跑，两份最终记录为修正后的运行。未将历史错误PASS算为最终通过。

通过范围是真实软件组件+fake VLM+SDK mocks的本地模拟。真实模型自由规划、GO2-W连接/运动/感知/导航都未验证。工程集成和生命周期修复不是论文创新。
