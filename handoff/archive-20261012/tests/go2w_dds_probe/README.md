# GO2-W laptop DDS state probe

This probe uses official Unitree SDK2 and only creates subscribers for
`rt/lf/sportmodestate` and `rt/lowstate`. It prints at most three samples from
each topic, waits at most 15 seconds, and exits. There is no publisher,
SportClient, or motion API in the source.

Build against the workspace-local SDK2 install:

```bash
cmake -S tests/go2w_dds_probe -B tests/go2w_dds_probe/build \
  -DCMAKE_PREFIX_PATH="$PWD/third_party/unitree_sdk2/install"
cmake --build tests/go2w_dds_probe/build
```

Run from the laptop while `enp131s0` has its confirmed `192.168.123.99/24`
address:

```bash
tests/go2w_dds_probe/build/go2w_dds_probe enp131s0
```

SDK2 checkout: `third_party/unitree_sdk2`; this probe is separate from the
vendor tree so its source and review remain independent of SDK examples.
