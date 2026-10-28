# Practical usage guide and examples

This guide explains how to configure HandoverLab 5G, run its trace-generation or trace-replay mode, and collect its outputs. The run now captures terminal output, bounds DDQN training with configurable limits, and automatically writes a completion report and algorithm-comparison PDF/CSV. It still does not calculate multi-seed statistics, standardized reliability, or measured handover interruption duration.

## 1. Set up and start the container

From `MAIN`, build the image once and start the service:

```sh
docker compose build
docker compose up -d
docker compose exec simulator bash
```

The compose file mounts the Python source, scenario inputs, waypoint inputs, and `handover-simulator/traces` from the host. Generated traces therefore remain visible on the host under `MAIN/handover-simulator/traces/`. If you already have a container from the previous compose file, recreate it to apply the new mounts:

```sh
docker compose up -d --force-recreate
docker compose exec simulator bash
```

No ns-3 rebuild is needed just to apply these volume mounts. If you rebuild or recreate from a newly built image, Docker may need to repeat the expensive ns-3 image build depending on its cache.

Inside the container:

```sh
cd /app/handover-simulator/src
python3 main.py --help
```

The project's expected default working directory is `handover-simulator/src`; relative default paths and `logging.conf` resolution depend on it.

## 2. Example files

The companion examples live in [`examples/`](examples/):

- [`quick.yaml`](examples/quick.yaml): shorter run, one UE, default input files.
- [`baseline.yaml`](examples/baseline.yaml): explicit baseline settings for the default scenario.
- [`seed-202.yaml`](examples/seed-202.yaml): another base seed for a separate repeat.
- [`custom-example.yaml`](examples/custom-example.yaml): points at the custom scenario and waypoint examples below.
- [`scenario-example.txt`](examples/scenario-example.txt): compact two-band, four-gNB scenario.
- [`waypoints-example.txt`](examples/waypoints-example.txt): waypoint graph with spawn points, legal paths, and a speed range.

Copy an example YAML into a convenient location and edit the values. Config paths are resolved from the process current directory. When running inside the usual `src` directory, use the provided `../../handover-simulator/...` paths or absolute paths.

Run a YAML configuration:

```sh
python3 main.py --config ../../documentation/examples/quick.yaml
```

For the paired custom scenario and waypoint example, run `python3 main.py --config /app/documentation/examples/custom-example.yaml` in the container.

The code applies YAML entries after parsing command-line options, so YAML values for recognized argument names override command-line values. Unrecognized YAML keys are ignored. Keep YAML keys exactly as parser attribute names (for example `simTime`, `nUEs`, `seed`, `sc`, `wp`).

`python3 main.py --help` also lists `--ddqnEpisodes` and `--ddqnTimeLimit`. In YAML use `ddqnEpisodes` and `ddqnTimeLimit`. The defaults are five episodes and a 120-second training budget; the time limit is checked between simulation intervals. `ddqnTimeLimit: 0` disables the time limit, while episode count remains the cap. A single DDQN batch already in progress can finish after the configured limit. The final DDQN evaluation pass is separate from training and also takes time.

## 3. Configure the scenario

The scenario file defines rectangular bounds, frequency bands, and gNB records. Lines beginning with `!` define bounds; `*` defines a band; other non-comment rows define gNBs:

```text
! minX maxX minY maxY
*0 3.5e9 20e6 100e6
*1 28e9 100e6 400e6
0 -100 0 10 0 30 I
1 0 100 10 0 30 I
2 100 0 10 1 23 I
3 0 -100 10 1 23 I
```

Fields are `Band_ID center_frequency_Hz user_bandwidth_Hz gNB_bandwidth_Hz` for a band and `GNB_ID X Y Z Band_ID tx_power_dBm type` for a gNB. The Python parser uses band IDs as list indices when classifying bands, so use contiguous IDs starting from 0 and define bands in matching order. gNB IDs are expected to correspond to their positions in the gNB list because trace directories are indexed from 0 to `nGnb - 1`.

Use `--sc /path/to/scenario.txt` (or `sc:` in YAML) to select a scenario. Keep the scenario and waypoint inputs in LF line-ending format. The bundled C++ parsers do not robustly ignore Windows CRLF blank lines; this caused the failure reported in the user's run and is why `MAIN`'s default input files were normalized to LF.

## 4. Configure waypoint mobility

The waypoint input has four exact section headers:

```text
WAYPOINTS
0 -100 0 1.5
1 0 0 1.5
2 100 0 1.5
SPAWN_POINTS
0
2
LEGAL_PATHS
0 2 2 1 2
2 0 2 1 0
SPEED_INTERVAL
1 2
```

Waypoint records are `id x y z`; spawn rows contain a waypoint ID; each legal path is `from to waypoint_id waypoint_id...` with no count prefix; speed interval is `min max` in m/s. The example file illustrates the parser's existing grammar. The C++ waypoint branch uses the speed interval to choose velocity; `speed` is also passed to ns-3 but does not replace this interval. Select the file with `wp:` in YAML or `--wp`. The default YAML/CLI configuration passes a waypoint file to ns-3. To disable waypoint-based movement, set `wp: null` in YAML; the Python code then omits `--wp`, and ns-3 uses its non-waypoint mobility branch. Verify this mode is suitable for your experiment before relying on it.

For waypoint simulations, set `simTime` long enough for the movement duration you want to evaluate. The current source help text says `simTime: 0` can derive duration from waypoints, but the exact behavior depends on the C++ mobility implementation; inspect outputs before using this as a reproducibility assumption.

## 5. Main configuration choices

The parser exposes these settings (the C++/Python code is authoritative; original docs may have drift):

| Key | Meaning |
|---|---|
| `simTime` | Duration in seconds (default 10). |
| `nUEs` | Number of UE trace sets (default 5). |
| `seed` | Base seed; Python passes `seed + UE index` to each ns-3 process. |
| `int` | Trace sampling interval in seconds in Python; converted to microseconds for ns-3. |
| `sc`, `wp` | Scenario and waypoint input paths. |
| `speed`, `trayectoryTime`, `tolerance` | Mobility inputs passed to ns-3. |
| `packetSize`, `bitRate`, `MaxPackets` | UDP traffic settings passed to ns-3. `MaxPackets: 0` is the existing unlimited default. |
| `errorModel` | PHY error model string passed to ns-3. |
| `Hys`, `A3Offset`, `ttt`, `NrMeasureInt`, `HOInterval` | Inputs used by the 3GPP event/handover simulations. |
| `alpha`, `beta` | Inputs passed to SBGH scoring; inspect `scoring.py` for actual use. |
| `logging` | ns-3 component logging flag. |
| `trace` | Existing trace directory to replay; this mode loads values from that trace's `parameters.json`. |
| `ddqnEpisodes` | Maximum DDQN training episodes (default 5). |
| `ddqnTimeLimit` | DDQN training budget in seconds (default 120; zero disables the time limit). |

The handover penalty in `main.py` is currently set to 20 ms for `Latency`; it is not a CLI/YAML option. Change scenario geometry, carrier frequencies, bandwidths, number/placement of gNBs, mobility paths, offered traffic, sampling interval, and algorithm parameters only with a recorded rationale. Preserve every YAML and input file used for a run with its outputs.

## 6. Run a reproducible set of seeds

The program writes a timestamp-named run directory. It stores `parameters.json`, `experiment.json`, copies of used inputs in `inputs/`, and `run.log`. Keep the config and code revision with each seed run; `experiment.json` records effective settings and the input snapshot path.

Run one seed at a time and wait for completion between invocations:

```sh
python3 main.py --config ../../documentation/examples/baseline.yaml
python3 main.py --config ../../documentation/examples/seed-202.yaml
```

Each run gets a separate timestamp folder under `handover-simulator/traces/`; the configured base seed is recorded in parameters. If a one-second timestamp collision occurs, the source does not create a unique suffix; wait until the next second before starting the next run.

There is no built-in multi-seed aggregator. The automatically generated comparison covers algorithms within one run, not uncertainty across seeds. Collect the run-level `algorithm_comparison.csv` files and calculate multi-seed summaries separately.

## 7. Read outputs and compare algorithms

For each run, the source expects:

```text
traces/<timestamp>/
├── parameters.json
├── experiment.json
├── inputs/                    # scenario, waypoint and supplied YAML copies
├── run.log                    # terminal output including DDQN progress
├── <UE index>/<gNB index>/traces.csv
└── results/
    ├── 3GPP_A3/scenario.csv
    ├── 3GPP_REL16_CHO/scenario.csv
    ├── SBGH/scenario.csv
    ├── ideal-SBGH/scenario.csv
    └── DDQN/scenario.csv
    # plus per-UE/gNB detail CSVs and DDQN reward/model files
├── Final_Report.pdf
├── Algorithm_Performance.pdf
├── algorithm_comparison.csv
└── run_status.json
```

Inspect CSV headers before analysis. The summary reads each algorithm's `scenario.csv` and reports mean throughput, mean latency, mean packet-loss fraction, handover counts where available, and the algorithm scenario score. PDF charts compare these saved aggregates; the final PDF includes run status, input/config summary, a flow diagram, completion-log highlights, algorithm completeness, and DDQN reward history when present. Missing algorithm result files are identified as incomplete in `run_status.json` and the PDFs. Reports do not make statistical claims beyond this run.

| Planned study output | Existing project support |
|---|---|
| Reproducible scenarios | Parameter manifest and snapshots of selected scenario, waypoint, and YAML inputs are saved per run. Archive the project revision as well. |
| Signal-based baseline | Rel.15 A3 and Rel.16 CHO implementations are present. |
| Learned handover model | DDQN implementation is present and run by the normal Python pipeline. |
| Multi-seed evaluation | You can rerun with different `seed` values; no batch runner or multi-seed summary is included. |
| Reliability, interruption, throughput comparison | CSV outputs include handovers, packet loss and throughput/latency-related values, but the project does not define a unified reliability score or a standalone interruption-duration metric/report. |
| Performance analysis and visualizations | Per-run metric summaries, bar charts, PDFs, and CSV comparison are now generated at the end of a successful Python algorithm pass. Multi-seed aggregation and confidence intervals are not included. |
| Final technical report/demo | `Final_Report.pdf` documents the completed run, selected configuration, output status, available metrics, log events, and interpretation caveats. A research presentation/demo still requires human review and explanation. |

For a multi-seed study, define fixed scenario/mobility inputs; archive the config and code revision; run several seeds; check each `run_status.json`; and aggregate the per-run comparison CSVs with a declared statistical method. Do not call handover count alone “reliability” or treat the fixed latency penalty as measured interruption duration without a validated metric definition.

## 8. Replay existing traces

From `src`, run:

```sh
python3 main.py --trace /app/handover-simulator/traces/<timestamp> \
  --sc /app/handover-simulator/scenario/sc.txt
```

Replay requires `parameters.json` and a CSV for every UE/gNB pair described by those parameters and the selected scenario. It skips ns-3 generation but runs all Python algorithms again. Replaying into the same run tree may overwrite algorithm results.

## 9. Check a run before analysis

From the container:

```sh
find /app/handover-simulator/traces/<timestamp> -name traces.csv -type f
find /app/handover-simulator/traces/<timestamp>/results -name scenario.csv -type f
ls -lh /app/handover-simulator/traces/<timestamp>/*.pdf
cat /app/handover-simulator/traces/<timestamp>/run_status.json
cat /app/handover-simulator/traces/<timestamp>/parameters.json
```

There should be `nUEs × nGnb` trace CSV files before Python begins algorithm evaluation. If they are missing, inspect the ns-3 output and exit status; “NS3 simulations finished” only indicates that Python worker tasks ended, not that all ns-3 jobs succeeded. See [troubleshooting](troubleshooting.md).
