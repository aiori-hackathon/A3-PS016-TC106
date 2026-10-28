# Troubleshooting

## Python import error when running `main.py`

Run from `handover-simulator/src` and install a compatible dependency set. The entry point imports TensorFlow, matplotlib, YAML and pandas at startup, including for trace replay. `handover-simulator/requirements.txt` lists only pandas; the root pinned requirements are the fuller supplied set. On Windows, TensorFlow/CUDA/TensorRT packages may not be installable as pinned; the checked-in Dockerfile targets Ubuntu 24.04.

## Scenario or waypoint file not found

The default paths are relative to the current working directory. Change to `handover-simulator/src`, or pass absolute paths with `--sc` and `--wp`. Confirm files exist at `scenario/sc.txt` and `waypoints/wp.txt` within the project.

## `NS3 simulations finished` followed by missing `traces.csv`

The Python message only means its worker tasks have ended; the current launcher does not fail fast when an ns-3 child exits unsuccessfully. In the reported run, `traces/2026-10-28_16-35-15/` contained `parameters.json` and UE/gNB directories but no CSVs. Re-running the ns-3 command directly showed `Reading .../scenario/sc.txt...` followed by `Failed to parse line:` and exit code 1. The scenario file had Windows CRLF line endings; its visually blank lines were read as a single `\r`, and the C++ parser attempted to parse them as gNB records. The waypoint parser also compares section names exactly and is sensitive to CRLF.

`MAIN/handover-simulator/scenario/sc.txt` and `waypoints/wp.txt` were normalized to LF without changing their text content. To apply them to an already-running container, either normalize the container copies and rerun:

```sh
sed -i 's/\r$//' /app/handover-simulator/scenario/sc.txt /app/handover-simulator/waypoints/wp.txt
cd /app/handover-simulator/src
python3 main.py
```

Or recreate the Compose service so the updated LF inputs and trace-output folder are mounted from the host:

```sh
docker compose up -d --force-recreate
docker compose exec simulator bash
```

Afterward, check the ns-3 child output and verify one CSV exists for each Python UE/gNB pair before processing. The rerun creates a new timestamp directory; the failed folder does not contain traces to replay.

The Compose file now mounts `handover-simulator/traces` to persist outputs. An older container created with the previous Compose definition has no such mount, so its existing trace directory is inside the container and not visible under the host project.

## ns-3 executable/build command not found

The Python code expects an ns-3 checkout at a sibling directory named `ns-3-dev`, with the network simulator available under `scratch/network-simulator` and an optimized ns-3.48 binary under `build/scratch/network-simulator`. The supplied Dockerfile creates this layout and compiles it. Confirm the ns-3 version, 5G-LENA v5.1 installation and successful ns-3 build.

## Trace replay reports missing parameters or CSVs

The trace path must contain `parameters.json` with fields the program reads, plus a `traces.csv` for each configured UE and scenario gNB index. Check that `--trace` points to the run root, not its `results` directory, and that `--sc` describes the same gNB count/order.

## Docker build runs out of memory

The compose definition passes `NS3_BUILD_JOBS=4` to reduce peak compiler memory. The Dockerfile notes roughly 2 GB per parallel job for 5G-LENA translation units. Lower the build arg if the Docker VM is memory-limited; do not run simultaneous builds on a constrained host.

These diagnoses correspond to source path assumptions and declared dependencies. The scenario parse failure was reproduced in the running container; the LF correction was validated with the same simulator binary.
