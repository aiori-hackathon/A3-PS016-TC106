# Configuration and input files

## CLI and YAML

The entry point is `handover-simulator/src/main.py`. Its parser defines `--simTime` (10), `--logging` (0), `--MaxPackets` (0), `--packetSize` (1000), `--bitRate` (380,000,000), `--seed` (1234), `--nUEs` (5), `--int` (0.1 seconds), `--errorModel` (`ns3::NrEesmCcT1`), `--sc`, `--wp`, `--speed` (10), `--trayectoryTime` (5), `--tolerance` (1), `--Hys` (5), `--NrMeasureInt` (0.1), `--A3Offset` (3), `--ttt` (0.1), `--HOInterval` (0.1), `--alpha` (5000), `--beta` (1000), `--trace`, and `--config`.

Defaults for `--sc` and `--wp` are `../../handover-simulator/scenario/sc.txt` and `../../handover-simulator/waypoints/wp.txt`, resolved relative to the process current directory. Run from `handover-simulator/src` for these defaults. A YAML mapping loaded by `--config` updates matching parser attributes after argument parsing; matching YAML keys therefore override CLI values. Unknown keys are ignored. The actual parameters supported by replay are read from the trace's `parameters.json`.

## Scenario format

`scenario/sc.txt` uses `!` followed by min/max X/Y dimensions, `*` followed by band ID, center frequency, user bandwidth and gNB bandwidth, then gNB rows containing ID, XYZ, band ID, transmit power and type. The Python parser turns these into dimension, band and gNB structures. The C++ parser also consumes the same file. See the original [scenario format guide](../docs/scenario-format.md) for syntax examples.

## Waypoint format

`waypoints/wp.txt` holds sections `WAYPOINTS`, `SPAWN_POINTS`, `LEGAL_PATHS` and `SPEED_INTERVAL`. Waypoint rows have an ID and XYZ; paths give source, destination, then waypoint IDs. C++ uses this when a waypoint path is supplied. Python's default passes the file into each generated ns-3 process.

## Trace and outputs

Each trace pair is stored at `<run>/<ue>/<gnb>/traces.csv`; `parameters.json` records selected run settings. Python expects cumulative columns such as packet/byte/loss counters and `Time`, and derives deltas and throughput. Algorithm result folders are `3GPP_A3`, `3GPP_CHO`, `SBGH`, `ideal-SBGH`, and `DDQN` beneath `<run>/results/`.

The source also sets a 20 ms `Latency` penalty in `main.py`. Not every parameter documented in original docs is exposed as a CLI flag; use the source parser as authoritative.
