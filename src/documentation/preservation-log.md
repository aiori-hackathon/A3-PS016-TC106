# Change and preservation log

## Copy

Source: `5g-handover-sim/`. Destination: `MAIN/`. `MAIN` was empty at inspection. Robocopy copied the 44 non-generated project files and retained directory structure, including source code, test suite, scenario/waypoint data, original docs, license/citation, PDF, Docker and CI files.

The source `.git/` directory was excluded because version-control history and metadata are not required to build or run the standalone project. Python `__pycache__` directories and `.pyc` files were excluded as generated interpreter artifacts; they are recreated by Python and are not source inputs.

## Compatibility and output-path changes

- `handover-simulator/scenario/sc.txt` and `waypoints/wp.txt` were converted from CRLF to LF in `MAIN`. Their text content is unchanged. This is needed because the existing C++ parsers treat CRLF blank lines as data and fail to match waypoint section headers. The original source copies were not changed.
- `docker-compose.yml` now bind-mounts scenario and waypoint directories read-only and the trace directory read/write. This makes the corrected inputs available in the existing image without rebuilding ns-3 and persists generated traces on the host.
- At the start of this diagnostic, `MAIN/dockerfile` already differed from the designated source: it included `build-essential` and `make` and had a changed ns-3 comment. Those existing destination differences were preserved; their origin was not established.

## Added files

- `README.md`: concise standalone entry point and links.
- `documentation/architecture.md`, `source-code.md`, `installation.md`, `build-execution.md`, `configuration-inputs.md`, `testing.md`, `troubleshooting.md`, `preservation-log.md`, `quick-start.md`, and `usage-guide.md`: explanatory docs based on inspected files.
- `documentation/examples/`: example YAML configurations plus scenario and waypoint text inputs.

The original `readme.md` is preserved byte-for-byte as `source-readme.md`; Windows cannot store distinct `README.md` and `readme.md` paths in one directory. The new concise root `README.md` therefore occupies the case-insensitive `readme.md` path. No application source files were changed. The two input line-ending changes and Compose volume changes are listed above. No new application features or tests were added.

## Subsequent implementation changes

- Added `terminal_log.py` to mirror Python stdout/stderr to a persistent session log and the active run's `run.log`. The Python entry point echoes ns-3 subprocess output so it is included in run logs.
- Added bounded DDQN episode/time controls and a terminal progress display. Defaults are five episodes and 120 seconds; this is a quick workflow default, not a convergence setting.
- Added per-run experiment/input snapshots and report generation for `Final_Report.pdf`, `Algorithm_Performance.pdf`, `algorithm_comparison.csv`, and `run_status.json`.
- Updated `main.py` to validate ns-3 return codes and propagate algorithm errors into final status.
- Updated documentation with current Linux/Docker usage, example configurations, RFC-2330 security/privacy boundaries and validation evidence.

## Verification

In the open Linux container, the unit suite passed (69 tests). A fresh run generated eight non-empty traces, all five algorithm outputs, both PDFs and a `COMPLETE` status; the DDQN loop completed six episodes in 12.051 seconds. A saved-trace replay also generated all expected 40 trace files and five algorithm outputs. The original CRLF parsing failure was reproduced and corrected by LF normalization. These smoke checks do not establish multi-seed performance, statistical significance, or DDQN convergence. See [testing](testing.md).

