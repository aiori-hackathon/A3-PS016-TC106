# HandoverLab 5G | Project Final Report

## Project identity

**HandoverLab 5G (HL5G)** is the project name used for the integrated workflow in this repository. The project combines an ns-3/5G-LENA cellular network simulation with Python handover evaluation. It is intended to reduce the manual integration work involved in generating UE/gNB traces and feeding comparable inputs to the project's handover policies. This report makes no claim that no other simulation tools exist.

## What the software provides

- Scenario, band, base-station, traffic, and waypoint configuration through text inputs, command-line values, and YAML.
- ns-3/5G-LENA simulation to create radio and packet-flow traces, organized by UE and gNB.
- Trace replay so Python policies can be evaluated again without repeating the network simulation.
- Five result paths: 3GPP Rel.15 A3, 3GPP Rel.16 CHO, SBGH, ideal-SBGH, and multi-agent DDQN.
- Per-run snapshots of active configuration and input files.
- Console mirroring to session and run logs; ns-3 subprocess output is echoed into the run log.
- DDQN episode progress, tunable maximum episode count, and a tunable training time budget.
- Completion and algorithm-comparison PDFs, comparison CSV, DDQN training history, algorithm result CSVs, and an explicit complete/partial run status.

The generated PDFs summarize one run. Multi-seed aggregation, confidence intervals, formal statistical tests, independent validation of reliability metrics, and an externally assessed technical demonstration remain research/reporting work beyond this implementation.

## Linux execution and verified run

The target runtime is Linux. The supplied Dockerfile uses Ubuntu 24.04, ns-3 3.48, and 5G-LENA 5.1. The running container used for validation was `main-simulator-1` on 2026-10-28.

The saved run at `handover-simulator/traces/2026-10-28_16-52-25/` contained 40 non-empty ns-3 trace CSVs (five UE indexes × eight gNB indexes) for a 10-second simulation with 0.1-second sampling and base seed 1234. The original run stopped before DDQN completed. I replayed its saved traces through all five algorithms using a two-episode DDQN smoke-training setting. The DDQN training loop recorded two episodes in 18.9 seconds. The full Python replay exited successfully and generated:

- `Final_Report.pdf`
- `Algorithm_Performance.pdf`
- `algorithm_comparison.csv`
- `run_status.json` with status `COMPLETE`
- `run.log`, `experiment.json`, input snapshots, DDQN rewards, weights, and algorithm detail CSVs

This verifies the replay and reporting pipeline for that run. Two DDQN training episodes are only a runtime smoke test; they do not establish policy convergence or scientific performance. The comparison is for one seed/run and is not a multi-seed conclusion.

A fresh end-to-end run was then completed inside the open Linux container at `handover-simulator/traces/2026-10-28_18-02-31/`: `--simTime 2 --nUEs 1 --seed 7 --ddqnEpisodes 6 --ddqnTimeLimit 90`. ns-3 produced eight non-empty UE/gNB trace CSVs. All five algorithms wrote their scenario result CSVs, DDQN completed six episodes in 12.05 seconds, and `run_status.json` reported `COMPLETE` with no algorithm errors. Both PDFs and the comparison CSV were generated. This small run confirms that fresh trace generation, evaluation and PDF creation connect successfully; it is not a representative performance benchmark.

The prior trace set's existing scenario aggregates before DDQN replay were: A3 and Rel.16 CHO about 1,596 Mbps mean aggregate throughput; SBGH and ideal-SBGH about 1,879 Mbps. Their CSV latency means were about 8.20 ms and 6.48 ms respectively. These are observed values from a single simulated run, before DDQN was added to the comparison; they are not statistical or real-network guarantees. The final comparison PDF/CSV generated after replay contains all five algorithms.

## DDQN runtime controls

The entry point now accepts `--ddqnEpisodes` and `--ddqnTimeLimit` (YAML keys `ddqnEpisodes` and `ddqnTimeLimit`). The defaults are five episodes and 120 seconds. Training prints an episode progress bar and records timing/stop reason in `results/DDQN/ddqn_training.json`. A training time limit is checked between intervals, so one currently running neural-network update may finish after the limit. DDQN's final trace-evaluation pass is additional to its training time.

For a quick workflow check, use a small episode count. For performance claims, tune training using held-out seeds and report the episode/time settings; do not describe quick-run weights as converged without evidence.

## RFC-2330 and security/privacy

RFC 2330 describes IP performance metrics and specifically warns that active measurements may be abused as denial-of-service traffic disguised as measurement, passive measurements may expose traffic contents, and each metric/methodology needs a security discussion. It has later updates; see [RFC 2330](https://www.rfc-editor.org/rfc/rfc2330.html) and [RFC 7679](https://www.rfc-editor.org/rfc/rfc7679.html) for measurement-specific security guidance.

HL5G is a simulator, not a live network measurement system. Its simulated UDP traffic is run inside ns-3, and the checked-in trace format records counters, RSRP, position and timing fields rather than packet payload. The five handover algorithms make serving-cell decisions; they do not detect DoS-like test traffic, authorize measurements, rate-limit live probes, encrypt data, or anonymize trace contents. They therefore do not directly protect users from either threat. Location, signal and timing records can still be sensitive and should be access-controlled before sharing.

An RFC-aligned future study should define each metric's entity, direction, units, sampling, traffic type, loss handling and calibration; assess active probe rate/scope/authorization; and document privacy, minimization, retention, access, and integrity controls. The [security and RFC guide](documentation/security-and-rfc2330.md) explains the distinction between current features and future controls. No RFC requirement or compliance claim is asserted for this project.

## Known limitations and unverified work

- The fresh end-to-end check used one UE, a two-second simulation, one seed and six DDQN episodes; its timing and performance values are only smoke-run observations.
- DDQN training quality and convergence were not assessed.
- The system generates per-run algorithm comparisons, but no multi-seed aggregator or confidence-interval analysis.
- Handover counts, packet loss, throughput and latency-related CSV values are available. There is no dedicated standardized reliability metric or independent interruption-duration measurement; the fixed latency penalty must not be presented as a measured interruption duration without validation.
- The project runs offline ns-3 scenarios and has no live-network safety controls, traffic authorization, result authentication, file encryption, anonymization, or retention enforcement.
- The Python unit suite passed in the container: 69 tests. A prior saved-trace replay and the fresh ns-3-to-report run both completed. No multi-seed batch or live-network test was performed.

## Project documents

- [Main README](README.md)
- [Complete usage guide and examples](documentation/usage-guide.md)
- [Testing and validation](documentation/testing.md)
- [Security and RFC-2330 notes](documentation/security-and-rfc2330.md)
- [Preservation log](documentation/preservation-log.md)
