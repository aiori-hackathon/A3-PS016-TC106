# HandoverLab 5G

**HandoverLab 5G (HL5G)** is an integrated ns-3/5G-LENA and Python workflow for generating cellular simulation traces and evaluating five handover result sets: 3GPP Rel.15 A3, 3GPP Rel.16 CHO, SBGH, ideal-SBGH, and DDQN.

## What the workflow automates

The project connects scenario and waypoint inputs to ns-3 trace generation, then feeds the same saved UE/gNB traces to the handover algorithms. That removes much of the per-experiment glue researchers would otherwise need to write to launch ns-3/5G-LENA runs, collect files, and call each policy implementation. Traces can be replayed without running ns-3 again.

- Configure run parameters through the CLI or YAML.
- Define network geometry, bands, base stations, and waypoint mobility in text inputs.
- Generate and retain trace CSVs per UE and gNB.
- Evaluate A3, CHO, SBGH, ideal-SBGH, and DDQN from the same trace set.
- Tune DDQN training episodes and time budget, with console progress and logs.
- Create a completion report PDF, an algorithm comparison PDF, and a comparison CSV when the Python pipeline finishes.
- Preserve the effective configuration and input copies with each run.

This name describes the project as a unified workflow; it does not claim that no other cellular simulators or research tools exist.

## Linux and Docker quick start

The supported container environment is Ubuntu 24.04 with ns-3 3.48 and 5G-LENA 5.1. From this directory on a host with Docker and Compose:

```sh
docker compose up -d --build
docker compose exec simulator bash
cd /app/handover-simulator/src
python3 main.py --help
python3 main.py
```

The full default run may be resource-intensive. At completion, check the timestamp folder beneath `/app/handover-simulator/traces/`; the Compose configuration mounts it back to this project. The primary report is `Final_Report.pdf`; `Algorithm_Performance.pdf`, `algorithm_comparison.csv`, `run.log`, and `run_status.json` accompany it.

Example run with bounded DDQN training:

```sh
python3 main.py --config /app/documentation/examples/quick.yaml --ddqnEpisodes 5 --ddqnTimeLimit 120
```

Training duration is configurable; few episodes are useful for a smoke run, not a convergence claim. See the [usage guide](documentation/usage-guide.md) for examples, input formats, seeds, outputs, and interpretation limits.

## Project components

- `network-simulator/`: C++ ns-3/5G-LENA radio and traffic simulation.
- `handover-simulator/src/`: Python trace loader, algorithms, DDQN agent, terminal log and report generation.
- `handover-simulator/scenario/` and `waypoints/`: default inputs.
- `docs/`: source project documentation; `documentation/`: operating guides and examples.

## Guides

- [Complete usage guide](documentation/usage-guide.md)
- [Quick start](documentation/quick-start.md)
- [Architecture](documentation/architecture.md)
- [Source code](documentation/source-code.md)
- [Installation](documentation/installation.md)
- [Build and execution](documentation/build-execution.md)
- [Configuration and inputs](documentation/configuration-inputs.md)
- [Testing and validation](documentation/testing.md)
- [Troubleshooting](documentation/troubleshooting.md)
- [RFC-2330 security and privacy notes](documentation/security-and-rfc2330.md)
- [Project final report](FINAL_REPORT.md)

The generated comparisons describe the saved run. The simulator does not itself establish statistical significance, a standardized reliability score, or measured handover interruption duration. The final report identifies these limits and distinguishes simulation results from live network measurements.
