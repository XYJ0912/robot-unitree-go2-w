#include <cstdint>
#include <exception>
#include <iostream>
#include <string>
#include <vector>

#include <unitree/robot/channel/channel_factory.hpp>
#include <unitree/robot/go2/video/video_client.hpp>

int main(int argc, char **argv) {
  if (argc < 2 || argc > 3 || (argc == 3 && std::string(argv[2]) != "--jpeg-stdout")) {
    std::cerr << "usage: go2w_camera_probe <network-interface> [--jpeg-stdout]\n";
    return 64;
  }
  try {
    unitree::robot::ChannelFactory::Instance()->Init(0, argv[1]);
    unitree::robot::go2::VideoClient video;
    video.SetTimeout(1.0f);
    video.Init();
    std::vector<std::uint8_t> bytes;
    const auto code = video.GetImageSample(bytes);
    const bool jpeg_markers = bytes.size() >= 4 && bytes[0] == 0xff &&
                              bytes[1] == 0xd8 && bytes[bytes.size() - 2] == 0xff &&
                              bytes[bytes.size() - 1] == 0xd9;
    if (argc == 3) {
      if (code == 0 && jpeg_markers && bytes.size() <= 4 * 1024 * 1024) {
        std::cout.write(reinterpret_cast<const char *>(bytes.data()), bytes.size());
      }
    } else {
      std::cout << "api_code=" << code << " bytes=" << bytes.size()
                << " jpeg_markers=" << (jpeg_markers ? "true" : "false") << '\n';
    }
    unitree::robot::ChannelFactory::Instance()->Release();
    return code == 0 && jpeg_markers && bytes.size() <= 4 * 1024 * 1024 ? 0 : 2;
  } catch (const std::exception &error) {
    std::cerr << "camera read-only probe failed: " << error.what() << '\n';
    return 1;
  }
}
