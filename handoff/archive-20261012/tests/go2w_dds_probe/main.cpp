#include <atomic>
#include <chrono>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <thread>

#include <unitree/idl/go2/LowState_.hpp>
#include <unitree/idl/go2/SportModeState_.hpp>
#include <unitree/robot/channel/channel_subscriber.hpp>

namespace {
std::atomic<int> high_count{0};
std::atomic<int> low_count{0};
std::mutex output_mutex;

void high_state(const void *raw) {
  const auto &state = *static_cast<const unitree_go::msg::dds_::SportModeState_ *>(raw);
  const int count = ++high_count;
  if (count > 3) return;
  const auto received_at = std::time(nullptr);
  std::lock_guard<std::mutex> lock(output_mutex);
  std::cout << "high topic=rt/lf/sportmodestate count=" << count
            << " received_unix_s=" << received_at
            << " device_stamp=" << state.stamp().sec() << "."
            << std::setw(9) << std::setfill('0') << state.stamp().nanosec()
            << " mode=" << static_cast<int>(state.mode())
            << " error_code=" << state.error_code()
            << " position_m=" << state.position()[0] << "," << state.position()[1]
            << "," << state.position()[2]
            << " yaw_rad=" << state.imu_state().rpy()[2] << std::endl;
}

void low_state(const void *raw) {
  const auto &state = *static_cast<const unitree_go::msg::dds_::LowState_ *>(raw);
  const int count = ++low_count;
  if (count > 3) return;
  const auto received_at = std::time(nullptr);
  std::lock_guard<std::mutex> lock(output_mutex);
  std::cout << "low topic=rt/lowstate count=" << count
            << " received_unix_s=" << received_at
            << " tick=" << state.tick()
            << " power_v=" << state.power_v()
            << " power_a=" << state.power_a()
            << " bms_soc_percent=" << static_cast<int>(state.bms_state().soc())
            << std::endl;
}
}  // namespace

int main(int argc, char **argv) {
  if (argc != 2) {
    std::cerr << "usage: go2w_dds_probe <network-interface>" << std::endl;
    return 64;
  }

  try {
    unitree::robot::ChannelFactory::Instance()->Init(0, argv[1]);
    unitree::robot::ChannelSubscriber<unitree_go::msg::dds_::SportModeState_> high(
        "rt/lf/sportmodestate");
    unitree::robot::ChannelSubscriber<unitree_go::msg::dds_::LowState_> low(
        "rt/lowstate");
    high.InitChannel(high_state, 1);
    low.InitChannel(low_state, 1);

    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(15);
    while (std::chrono::steady_clock::now() < deadline &&
           (high_count.load() < 3 || low_count.load() < 3)) {
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    high.CloseChannel();
    low.CloseChannel();
    unitree::robot::ChannelFactory::Instance()->Release();
    std::cout << "summary high=" << high_count.load()
              << " low=" << low_count.load() << std::endl;
    return high_count.load() > 0 || low_count.load() > 0 ? 0 : 2;
  } catch (const std::exception &error) {
    std::cerr << "DDS subscription failed: " << error.what() << std::endl;
    return 1;
  }
}
