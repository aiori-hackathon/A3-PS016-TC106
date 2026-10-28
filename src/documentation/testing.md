# Testing and validation

## Linux container validation performed (2026-10-28)

- `python3 -m pytest -q` in the open container: **69 passed**.
- Fresh integrated run from `/app/handover-simulator/src`: `python3 -u main.py --simTime 2 --nUEs 1 --seed 7 --ddqnEpisodes 6 --ddqnTimeLimit 90`. ns-3 emitted eight non-empty UE/gNB trace CSVs. All five algorithm scenario CSVs were generated; DDQN completed six episodes in 12.051 seconds. `run_status.json` reported `COMPLETE` with no algorithm errors. The run produced `Final_Report.pdf`, `Algorithm_Performance.pdf`, `algorithm_comparison.csv`, and `run.log`.
- Saved-trace replay produced all 40 expected trace files and all five algorithm results; a two-episode DDQN pass took 18.876 seconds.
- Reproduced the original parser failure with CRLF scenario inputs (exit 1), then verified LF-normalized inputs with the same ns-3 executable (exit 0 and non-empty traces). The project scenario/waypoint text files in this copy were normalized to LF.
- Docker Compose configuration and example YAML inputs were validated. The custom example scenario and waypoint file also ran through ns-3 and generated a non-empty trace.

The fresh run is a smoke test, not a multi-seed benchmark or evidence of DDQN convergence. It uses a short duration and a single UE. No live network test, statistical confidence interval, or formal interruption-duration validation was performed.

## Repository tests

The checked-in unit tests are in `handover-simulator/tests/`; `pytest.ini` sets this as `testpaths`. CI installs `requirements-dev.txt` and runs `pytest` from `handover-simulator`. With dependencies installed:

```sh
cd handover-simulator
python -m pip install -r requirements-dev.txt
python -m pytest
```

The tests cover fixtures and focused helper/simulator behavior; they do not run a full ns-3 network build or end-to-end simulation.

## Copy validation

- The source and destination roots were resolved as sibling directories; `MAIN` was empty before copying. Robocopy copied 44 project files without reported copy failures. `.git/` history and generated Python bytecode were excluded.
- `scenario/sc.txt` and `waypoints/wp.txt` were normalized from CRLF to LF. Their text content is unchanged; the C++ parsers otherwise treat CRLF blank lines as data and fail to match waypoint section headers. Original source copies were not modified.
- `docker-compose.yml` bind-mounts scenario and waypoint inputs read-only and traces read/write so the corrected inputs are used without rebuilding and generated outputs persist on the host.
- The existing ns-3 binary failed (exit 1) on the original CRLF scenario and succeeded (exit 0) with LF-normalized scenario and waypoint inputs, producing a non-empty CSV.

No fresh Docker image build, multi-seed batch, live network evaluation, confidence interval analysis, or formal interruption-duration validation was performed. Do not treat the smoke run as a benchmark or as evidence of DDQN convergence.
