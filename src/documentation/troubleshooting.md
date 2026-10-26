# Troubleshooting

## Python import error when running `main.py`

Run from `handover-simulator/src` and install a compatible dependency set. The entry point imports TensorFlow, matplotlib, YAML and pandas at startup, including for trace replay. `handover-simulator/requirements.txt` lists only pandas; the root pinned requirements are the fuller supplied set. On Windows, TensorFlow/CUDA/TensorRT packages may not be installable as pinned; the checked-in Dockerfile targets Ubuntu 24.04.

## Scenario or waypoint file not found

The default paths are relative to the current working directory. Change to `handover-simulator/src`, or pass absolute paths with `--sc` and `--wp`. Confirm files exist at `scenario/sc.txt` and `waypoints/wp.txt` within the project.

## ns-3 executable/build command not found

The Python code expects an ns-3 checkout at a sibling directory named `ns-3-dev`, with the network simulator available under `scratch/network-simulator` and an optimized ns-3.48 binary under `build/scratch/network-simulator`. The supplied Dockerfile creates this layout and compiles it. Confirm the ns-3 version, 5G-LENA v5.1 installation and successful ns-3 build.

## Trace replay reports missing parameters or CSVs

The trace path must contain `parameters.json` with fields the program reads, plus a `traces.csv` for each configured UE and scenario gNB index. Check that `--trace` points to the run root, not its `results` directory, and that `--sc` describes the same gNB count/order.

## Docker build runs out of memory

The compose definition passes `NS3_BUILD_JOBS=4` to reduce peak compiler memory. The Dockerfile notes roughly 2 GB per parallel job for 5G-LENA translation units. Lower the build arg if the Docker VM is memory-limited; do not run simultaneous builds on a constrained host.

These diagnoses correspond to source path assumptions and declared dependencies. No runtime failure was reproduced in the current environment.
