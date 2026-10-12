#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <thread>

#include <unitree/idl/go2/LowState_.hpp>
#include <unitree/idl/go2/SportModeState_.hpp>
#include <unitree/idl/ros2/PointCloud2_.hpp>
#include <unitree/robot/channel/channel_subscriber.hpp>

namespace {
std::mutex output_mutex;
std::atomic<unsigned> high_count{0};
std::atomic<unsigned> low_count{0};
std::atomic<unsigned> cloud_count{0};

std::int64_t unix_ns() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
             std::chrono::system_clock::now().time_since_epoch())
      .count();
}

std::int64_t monotonic_ns() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
             std::chrono::steady_clock::now().time_since_epoch())
      .count();
}

void number(double value) {
  if (std::isfinite(value)) {
    std::cout << std::setprecision(9) << value;
  } else {
    std::cout << "null";
  }
}

void high_state(const void *raw) {
  const auto received_unix_ns = unix_ns();
  const auto received_monotonic_ns = monotonic_ns();
  const auto &state = *static_cast<const unitree_go::msg::dds_::SportModeState_ *>(raw);
  const auto count = ++high_count;
  if (count > 10) return;
  std::lock_guard<std::mutex> lock(output_mutex);
  std::cout << "{\"source\":\"read_only_real\",\"topic\":\"rt/lf/sportmodestate\""
            << ",\"received_unix_ns\":" << received_unix_ns
            << ",\"received_monotonic_ns\":" << received_monotonic_ns
            << ",\"sequence\":" << count
            << ",\"device_stamp_sec\":" << state.stamp().sec()
            << ",\"device_stamp_nanosec\":" << state.stamp().nanosec()
            << ",\"mode\":" << static_cast<unsigned>(state.mode())
            << ",\"error_code\":" << state.error_code()
            << ",\"position_raw\":[";
  for (unsigned i = 0; i < 3; ++i) {
    if (i) std::cout << ',';
    number(state.position()[i]);
  }
  std::cout << "],\"velocity_raw\":[";
  for (unsigned i = 0; i < 3; ++i) {
    if (i) std::cout << ',';
    number(state.velocity()[i]);
  }
  std::cout << "],\"imu_rpy_raw\":[";
  for (unsigned i = 0; i < 3; ++i) {
    if (i) std::cout << ',';
    number(state.imu_state().rpy()[i]);
  }
  std::cout << "]}" << std::endl;
}

void low_state(const void *raw) {
  const auto received_unix_ns = unix_ns();
  const auto received_monotonic_ns = monotonic_ns();
  const auto &state = *static_cast<const unitree_go::msg::dds_::LowState_ *>(raw);
  const auto count = ++low_count;
  if (count > 10) return;
  std::lock_guard<std::mutex> lock(output_mutex);
  std::cout << "{\"source\":\"read_only_real\",\"topic\":\"rt/lowstate\""
            << ",\"received_unix_ns\":" << received_unix_ns
            << ",\"received_monotonic_ns\":" << received_monotonic_ns
            << ",\"sequence\":" << count
            << ",\"tick\":" << state.tick()
            << ",\"power_v\":";
  number(state.power_v());
  std::cout << ",\"power_a\":";
  number(state.power_a());
  std::cout << ",\"bms_soc_percent\":" << static_cast<unsigned>(state.bms_state().soc())
            << ",\"bms_status_raw\":" << static_cast<unsigned>(state.bms_state().status())
            << "}" << std::endl;
}

void cloud_state(const void *raw) {
  const auto received_unix_ns = unix_ns();
  const auto &cloud = *static_cast<const sensor_msgs::msg::dds_::PointCloud2_ *>(raw);
  const auto count = ++cloud_count;
  if (count > 3) return;
  std::lock_guard<std::mutex> lock(output_mutex);
  std::cout << "{\"source\":\"read_only_real\",\"topic\":\"rt/utlidar/cloud\""
            << ",\"received_unix_ns\":" << received_unix_ns
            << ",\"sequence\":" << count
            << ",\"stamp_sec\":" << cloud.header().stamp().sec()
            << ",\"stamp_nanosec\":" << cloud.header().stamp().nanosec()
            << ",\"frame_id\":\"" << cloud.header().frame_id() << "\""
            << ",\"height\":" << cloud.height()
            << ",\"width\":" << cloud.width()
            << ",\"point_step\":" << cloud.point_step()
            << ",\"fields\":[";
  for (std::size_t i = 0; i < cloud.fields().size(); ++i) {
    if (i) std::cout << ',';
    std::cout << '"' << cloud.fields()[i].name() << '"';
  }
  std::cout << "]}" << std::endl;
}
}  // namespace

int main(int argc, char **argv) {
  if (argc != 2) {
    std::cerr << "usage: go2w_readonly_capture <network-interface>\n";
    return 64;
  }
  try {
    unitree::robot::ChannelFactory::Instance()->Init(0, argv[1]);
    unitree::robot::ChannelSubscriber<unitree_go::msg::dds_::SportModeState_> high(
        "rt/lf/sportmodestate");
    unitree::robot::ChannelSubscriber<unitree_go::msg::dds_::LowState_> low("rt/lowstate");
    unitree::robot::ChannelSubscriber<sensor_msgs::msg::dds_::PointCloud2_> cloud(
        "rt/utlidar/cloud");
    high.InitChannel(high_state, 1);
    low.InitChannel(low_state, 1);
    cloud.InitChannel(cloud_state, 1);
    std::this_thread::sleep_for(std::chrono::seconds(10));
    high.CloseChannel();
    low.CloseChannel();
    cloud.CloseChannel();
    unitree::robot::ChannelFactory::Instance()->Release();
    std::cerr << "capture counts: high=" << high_count.load()
              << " low=" << low_count.load() << " cloud=" << cloud_count.load() << '\n';
    return high_count.load() > 0 && low_count.load() > 0 ? 0 : 2;
  } catch (const std::exception &error) {
    std::cerr << "read-only capture failed: " << error.what() << '\n';
    return 1;
  }
}
