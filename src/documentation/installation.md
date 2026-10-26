# Installation and prerequisites

## Recommended supplied route: Docker

The root `dockerfile` starts from Ubuntu 24.04, installs native build tools and libraries, creates a Python virtual environment, installs root `requirements.txt`, clones ns-3 branch/tag `ns-3.48` and 5G-LENA branch/tag `v5.1`, links this project's `network-simulator` under ns-3 `scratch`, and builds ns-3. Docker and Docker Compose are needed on the host. Build memory is significant; `docker-compose.yml` defaults to four build jobs.

From `MAIN`:

```sh
docker compose build
docker compose run --rm simulator
```

The service starts an interactive shell in `/app`. Its compose bind mount maps host `handover-simulator/src` to `/app/handover-simulator/src`; source data and code otherwise come from the image.

## Native route

The source README documents Ubuntu 24.04, Python 3.10+, ns-3 3.48 and 5G-LENA 5.1. The Python orchestrator derives the expected ns-3 directory as a sibling of the project root (`<parent>/ns-3-dev`) and expects the network module available at `ns-3-dev/scratch/network-simulator`. It does not install or configure those dependencies itself.

Install Python dependencies in a virtual environment from `MAIN`:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

For tests, install the project's development list from `handover-simulator` with `python -m pip install -r requirements-dev.txt` (this includes the runtime list and pytest/matplotlib). The source's compact handover requirements list only pandas, while `main.py` imports YAML, matplotlib and TensorFlow unconditionally, so the root pinned requirements are the supplied broad runtime environment. Root requirements include GPU/CUDA/TensorRT wheels and may not install on every platform; Docker is the repository's reproducible route.

No successful dependency installation was performed as part of this copy. See [validation status](testing.md).
