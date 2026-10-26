# Architecture and execution flow

## Layers

The C++ ns-3 application in `network-simulator/sim.cc` creates the radio simulation and periodically writes CSV measurements. It reads the scenario and optional waypoint files, configures bands, gNBs, UE mobility and UDP traffic, and collects FlowMonitor statistics. It depends on ns-3 and 5G-LENA APIs and is built as an ns-3 scratch program.

The Python application in `handover-simulator/src/main.py` parses CLI arguments and optional YAML values, reads the scenario to determine gNB count, then either launches the compiled ns-3 binary for each UE/gNB pair or loads a prior trace folder. It derives per-interval counter differences and throughput, runs A3, CHO, SBGH, ideal-SBGH, and DDQN routines, and writes algorithm result CSVs beneath the trace folder. Python traces are expected in `<trace>/<UE index>/<gNB index>/traces.csv`; replay also reads `parameters.json`.

## Flow details

1. The Python entry point loads `logging.conf`, parses arguments and scenario.
2. For generation, it resolves `ns-3-dev` as a sibling of the project root, builds `scratch/network-simulator/sim.cc`, then starts one ns-3 process for every UE/gNB pair. Runs use a timestamp folder under `handover-simulator/traces/`.
3. The C++ executable writes counters, RSRP, distance, and delay-related measurements at the configured sampling interval. The C++ input parser consumes the scenario and, when supplied, waypoint data.
4. Python loads the CSV matrix, calculates counter deltas and throughput, and executes algorithm simulators sequentially.
5. Each algorithm writes its own results under `<trace>/results/`; helper modules handle event tests, score calculation, gNB occupation/channel effects, and DDQN state/action processing.

`--trace` skips ns-3 generation and uses stored parameters and CSVs, but still parses the scenario from the current working directory-relative `--sc` path. The source's default paths assume the current directory is `handover-simulator/src`.

## Implementation scope

The four named algorithm families are present in Python modules. The source also includes a C++ network simulation layer. No claim of conformance beyond the behavior visible in this code is made here; consult [the algorithm notes](../docs/algorithms.md) and module implementations. The C++ path is not self-contained with this project alone: ns-3 and 5G-LENA are external build prerequisites.
