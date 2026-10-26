# 5G Handover Simulation

This project evaluates four handover procedures against radio and traffic traces. Its Python layer reads trace CSV files and writes per-algorithm results; an included C++ program for ns-3 and 5G-LENA can generate those traces.

## Components

- `network-simulator/`: ns-3 C++ trace generator (`sim.cc`, `sim.h`).
- `handover-simulator/src/`: Python trace processing, handover algorithms, and result writing.
- `handover-simulator/scenario/` and `waypoints/`: supplied scenario and mobility inputs.
- `docs/`: original project notes; `documentation/`: standalone operating and source guides.

## Quick start

The full workflow requires Linux (the supplied Dockerfile uses Ubuntu 24.04), Docker/Compose, and a Docker image build that installs ns-3 3.48, 5G-LENA 5.1, and Python requirements. From this directory:

```sh
docker compose up -d --build
docker compose run --rm simulator
cd /app/handover-simulator/src
python3 main.py --help
```

To run the default trace generation and algorithm workflow, use `python3 main.py` from `/app/handover-simulator/src`. This invokes ns-3 and can be resource intensive. Python-only replay requires an existing compatible trace directory; see [Quick start](documentation/quick-start.md).

## Documentation

- [Architecture](documentation/architecture.md)
- [Source code guide](documentation/source-code.md)
- [Installation](documentation/installation.md)
- [Build and execution](documentation/build-execution.md)
- [Configuration and inputs](documentation/configuration-inputs.md)
- [Testing and validation](documentation/testing.md)
- [Troubleshooting](documentation/troubleshooting.md)
- [Change and preservation log](documentation/preservation-log.md)
- [Quick start](documentation/quick-start.md)

The code implements Rel.15 A3, Rel.16 CHO, SBGH/ideal-SBGH, and a DDQN simulation path. Their implementation details and limitations are documented in the original [`docs/algorithms.md`](docs/algorithms.md). The native ns-3 path additionally needs an ns-3/5G-LENA checkout at the location described in the execution guide. Windows is not the documented native target.
