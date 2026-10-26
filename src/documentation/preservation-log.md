# Change and preservation log

## Copy

Source: `5g-handover-sim/`. Destination: `MAIN/`. `MAIN` was empty at inspection. Robocopy copied the 44 non-generated project files and retained directory structure, including source code, test suite, scenario/waypoint data, original docs, license/citation, PDF, Docker and CI files.

The source `.git/` directory was excluded because version-control history and metadata are not required to build or run the standalone project. Python `__pycache__` directories and `.pyc` files were excluded as generated interpreter artifacts; they are recreated by Python and are not source inputs.

## Added files

- `README.md`: concise standalone entry point and links.
- `documentation/architecture.md`, `source-code.md`, `installation.md`, `build-execution.md`, `configuration-inputs.md`, `testing.md`, `troubleshooting.md`, `preservation-log.md`, and `quick-start.md`: explanatory docs based on inspected files.

The original `readme.md` is preserved byte-for-byte as `source-readme.md`; Windows cannot store distinct `README.md` and `readme.md` paths in one directory. The new concise root `README.md` therefore occupies the case-insensitive `readme.md` path. No application source, source configuration, build scripts, tests, or other original documentation were modified. No new application features or tests were added. Documentation is additive. The original implementation files in `MAIN` are expected to match the source byte-for-byte; this expectation must be confirmed by the final checksum check.

## Verification limits

The available environment is Windows with Python 3.10.11, but pytest and TensorFlow are absent; no dependency installation, tests, native build, Docker build, trace generation, or output comparison was performed. Accordingly, runtime behavior and reproducibility are not claimed as verified. See [testing](testing.md).

