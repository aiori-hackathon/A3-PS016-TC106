# Build and execution

## Docker build

From `MAIN`, run `docker compose build`. The Dockerfile configures and compiles ns-3 3.48 with 5G-LENA 5.1 and the project's network simulator. Build job count is `NS3_BUILD_JOBS` (default four).

Start the shell with `docker compose run --rm simulator`. Inside the container:

```sh
cd /app/handover-simulator/src
python3 main.py --help
python3 main.py
```

The no-argument command performs ns-3 trace generation and then Python processing. It can start `nUEs × nGnb` simulator processes, waits ten seconds in each worker before launching its process, and uses all reported CPU cores as thread-pool capacity. This may require substantial CPU and memory.

## Native build

With ns-3 already installed at the expected sibling path and the project module linked at `ns-3-dev/scratch/network-simulator`, build from the ns-3 root:

```sh
./ns3 configure --build-profile=optimized
./ns3 build
```

Then, from `MAIN/handover-simulator/src`, run `python3 main.py`. The code itself invokes `ns3 build scratch/network-simulator/sim.cc` and executes the optimized ns-3.48 program. Paths for default scenario/waypoint files are relative to this source directory.

## Replaying existing traces

Provide a trace directory with `parameters.json` and numeric UE/gNB folders containing `traces.csv`:

```sh
cd /app/handover-simulator/src
python3 main.py --trace /path/to/run-folder
```

The scenario argument is still loaded; use `--sc` if needed. `--trace` skips ns-3 but does not skip imports of the runtime modules. Results are written under the supplied trace folder's `results/` subdirectories. The source README describes timestamped output under `handover-simulator/traces/` for generated runs.

For argument names and behavior, see [configuration and inputs](configuration-inputs.md). Commands above are derived from checked-in project instructions and code; they were not successfully executed in the current environment.
