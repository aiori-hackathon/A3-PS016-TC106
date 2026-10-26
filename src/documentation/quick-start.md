# Quick start

## Full run using the supplied Docker environment

Prerequisites: Docker Engine and Docker Compose, with enough memory for an ns-3/5G-LENA build. From `MAIN`:

```sh
docker compose up -d --build
docker compose run --rm simulator
cd /app/handover-simulator/src
python3 main.py
```

The final command generates ns-3 traces and then runs the Python algorithms. Output goes under `/app/handover-simulator/traces/`. Review [installation](installation.md) and [build/execution](build-execution.md) first.

## Replay prepared traces

In the container shell, use `python3 main.py --trace /path/to/run-folder` from `/app/handover-simulator/src`. Supply a compatible run folder containing `parameters.json` and per-UE/per-gNB CSVs. The scenario must also resolve correctly. This path still needs the Python runtime dependencies.

For native setup, parameters, tests, or known limitations see [installation](installation.md), [configuration and inputs](configuration-inputs.md), [testing](testing.md), and [troubleshooting](troubleshooting.md).
