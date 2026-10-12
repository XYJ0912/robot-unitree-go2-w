# Go2W read-only deployment preparation

This directory is separate from the Robonix monorepo and the Go2 deployment.
At present it contains a bounded native SDK2 DDS capture and a Robonix
commissioning profile with one real, on-demand camera snapshot primitive plus
an explicitly mock-only health primitive. No motion capability is declared.
`GO2_ALLOW_MOTION` remains false; no motion code is implemented.

Build against the laptop-local official SDK2 installation:

```sh
cmake -S . -B build -DCMAKE_PREFIX_PATH=../../third_party/unitree_sdk2/install
cmake --build build -j2
./build/go2w_readonly_capture enp131s0
./build/go2w_camera_probe enp131s0
```

The capture runs for ten seconds and prints at most ten JSON samples per
state topic and three metadata-only PointCloud2 samples from a candidate
`rt/utlidar/cloud` topic. It never prints point data. `*_raw` fields
deliberately do not claim a validated frame or unit.
`received_*` are laptop clocks, not source clocks. Exit 0 means both topics
were seen, 2 means one or both were absent.
The camera probe sends one SDK image-read request, prints only size/return
code/JPEG markers, and saves no image. It does not validate camera calibration
or authorize publishing an RGB capability.

The SDK2 Go2W example confirms `rt/lf/sportmodestate` but also calls motion
APIs; do not run that example on a shared robot. Before registering standard
Robonix odometry, IMU, health or sensor capabilities, validate frame, unit,
timestamp and mandatory-field semantics on this Go2W. In particular, the
current health contract's mandatory `charging` bool cannot represent unknown.

`robonix_manifest.yaml`, `soma.yaml` and the one-link URDF are an explicit
commissioning fixture. The health entry currently references the local
handoff package in `../robonix/examples/go2w_readonly`; it is not a portable
vendor deployment and must not be published as one. The one-link URDF is not a
Go2W description or TF calibration. The fixture must be replaced by an
independent real state provider package and a measured whole-robot URDF before
claiming a production robot deployment. The real camera snapshot reports
unknown source time and optical frame; it is for inspection, not geometry or
navigation.

For Robonix commissioning on this laptop, use `bash build.sh` and then
`bash start.sh` from this directory. These wrappers set the deployment path
used by the manifest, keep `GO2_ALLOW_MOTION=false`, and use package-local
environments. Stop `start.sh` with Ctrl-C. Atlas, Executor and Soma bind only
to `127.0.0.1`; the camera SDK binary uses `enp131s0` only for one read-only
image request per snapshot call (plus one readiness request at activation).
