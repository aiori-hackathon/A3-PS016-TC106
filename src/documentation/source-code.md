# Source code guide

## Python (`handover-simulator/src/`)

| File | Role and relationship |
|---|---|
| `main.py` | CLI/YAML entry point; builds/launches ns-3 or loads traces, derives metrics, invokes all algorithm routines. Imports TensorFlow, matplotlib, YAML, pandas, and project modules at startup. |
| `utils.py` | Scenario and trace loading, rate/frequency helpers, penalty application, terminal helper, shared constants. |
| `simulator_common.py` | Shared per-UE/per-gNB replay and aggregate/channel simulation routines. |
| `simulator_3gpp.py` | Rel.15 A3 simulation. Uses NR event helper, shared utilities and common aggregation. |
| `simulator_3gpp_rel16.py` | Conditional handover simulation. |
| `simulator_sbgh.py` | Score-based greedy and ideal-SBGH simulation paths. |
| `simulator_gti_dqn.py` | DDQN-based handover simulation and metric aggregation. |
| `scoring.py` | Candidate-cell scoring and aggregate score helpers used by SBGH. |
| `nrEvents.py` | A3 event-condition checks used by 3GPP paths. |
| `occupation.py` | Load, queue delay, throughput and packet-loss/channel calculations used by common simulation. |
| `environment.py` | State/reward/action environment used by DDQN. |
| `dqn.py` | Neural-network agent, replay memory, policy/target updates; uses TensorFlow/Keras. |
| `logging.conf` | Python logging configuration loaded by `main.py` from the current working directory. |

## C++ (`network-simulator/`)

| File | Role and dependencies |
|---|---|
| `sim.cc` | ns-3 executable: argument parsing, scenario/waypoint parsing, radio and traffic setup, periodic flow measurements and CSV output. Requires ns-3 and 5G-LENA headers/libraries. |
| `sim.h` | Structures and declarations shared by the simulation source, including scenario, movement, bands and measurement data. |
| `LICENSE` | License for the network simulator component. |

## Inputs, tests, and project files

- `handover-simulator/scenario/sc.txt`: default dimensions, band records and gNB placements.
- `handover-simulator/waypoints/wp.txt`: waypoint, spawn, legal-path and speed interval data.
- `handover-simulator/tests/`: pytest unit tests for utility, event, scoring, occupation, environment and simulator behavior. `conftest.py` provides fixtures; `pytest.ini` selects the test directory.
- `handover-simulator/requirements.txt`: runtime declaration (`pandas`); `requirements-dev.txt` adds the runtime list, pytest and matplotlib.
- Root `requirements.txt`: pinned, broad Docker Python package set including TensorFlow/Keras and CUDA/TensorRT packages.
- Root `dockerfile`, `docker-compose.yml`: Ubuntu image, dependencies, ns-3/5G-LENA checkout/build and interactive service.
- `.github/workflows/`: CI definitions for pytest and Docker image build.
- Root source README (preserved as `source-readme.md` because Windows paths are case-insensitive), `docs/`: source project documentation; `code_repo.pdf`: supplementary reference copied from source.
- `CITATION.cff`, `LICENSE` files: citation and component licensing information.

The project has no Python packaging metadata or installable package declaration. The scripts use local imports and are normally run from `handover-simulator/src`.

