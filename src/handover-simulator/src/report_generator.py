"""Create run and algorithm comparison PDFs from existing simulator outputs."""

import json
import math
import textwrap
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd


ALGORITHM_DIRS = {
    "3GPP A3": "3GPP_A3",
    "3GPP Rel.16 CHO": "3GPP_REL16_CHO",
    "SBGH": "SBGH",
    "Ideal SBGH": "ideal-SBGH",
    "DDQN": "DDQN",
}


def _finite_mean(frame, column):
    if column not in frame:
        return float("nan")
    values = pd.to_numeric(frame[column], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return float(values.mean()) if not values.empty else float("nan")


def _finite_sum(frame, column):
    if column not in frame:
        return float("nan")
    values = pd.to_numeric(frame[column], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return float(values.sum()) if not values.empty else float("nan")


def collect_algorithm_metrics(run_dir):
    rows = []
    frames = {}
    for label, folder in ALGORITHM_DIRS.items():
        csv_path = Path(run_dir) / "results" / folder / "scenario.csv"
        row = {"Algorithm": label, "Result status": "missing"}
        if csv_path.is_file():
            try:
                frame = pd.read_csv(csv_path)
                frames[label] = frame
                row["Result status"] = "available"
                row["Mean throughput (Mbps)"] = _finite_mean(frame, "Throughput") / 1e6
                row["Mean latency (ms)"] = _finite_mean(frame, "Latency") * 1e3
                row["Handover count"] = _finite_sum(frame, "Handovers")
                row["Mean packet loss (%)"] = _finite_mean(frame, "PLostPackets") * 100
                score_path = csv_path.parent / "scenario-score.txt"
                row["Scenario score"] = score_path.read_text(encoding="utf-8").strip() if score_path.exists() else ""
            except Exception as exc:  # preserve a report even for a malformed result file
                row["Result status"] = f"unreadable: {exc}"
        rows.append(row)
    return pd.DataFrame(rows), frames


def _write_comparison_csv(summary, run_dir):
    output = Path(run_dir) / "algorithm_comparison.csv"
    summary.to_csv(output, index=False)
    return output


def _report_text_page(pdf, title, sections, footer):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    fig.text(0.07, 0.95, title, fontsize=21, fontweight="bold", color="#17324d", va="top")
    y = 0.89
    for heading, body in sections:
        fig.text(0.07, y, heading, fontsize=12, fontweight="bold", color="#136f8a", va="top")
        y -= 0.027
        for line in body.splitlines():
            wrapped = textwrap.wrap(line, width=100) or [""]
            for part in wrapped:
                fig.text(0.075, y, part, fontsize=9, family="DejaVu Sans Mono" if line.startswith("+") or line.startswith("|") else "DejaVu Sans", va="top")
                y -= 0.019
        y -= 0.018
        if y < 0.10:
            break
    fig.text(0.07, 0.035, footer, fontsize=8, color="#666666")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _bar_page(pdf, summary, title, metrics):
    fig, axes = plt.subplots(2, 2, figsize=(11.7, 8.3))
    fig.suptitle(title, fontsize=18, fontweight="bold", color="#17324d")
    colors = ["#2878B5", "#53A3D3", "#38A77C", "#87C66E", "#E29B35"]
    for ax, (column, label, unit) in zip(axes.flat, metrics):
        values = pd.to_numeric(summary.get(column, pd.Series(dtype=float)), errors="coerce")
        valid = values.notna()
        names = summary.loc[valid, "Algorithm"].tolist()
        vals = values[valid].to_numpy()
        if len(vals):
            bars = ax.bar(names, vals, color=colors[:len(vals)])
            ax.bar_label(bars, fmt="%.3g", padding=3, fontsize=8)
            ax.tick_params(axis="x", labelrotation=24, labelsize=8)
            ax.margins(y=0.18)
        else:
            ax.text(0.5, 0.5, "No complete result values", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(label, fontsize=11)
        ax.set_ylabel(unit)
        ax.grid(axis="y", alpha=0.25)
    fig.text(0.04, 0.025, "Higher throughput is generally better. Handover count alone is not a reliability measure; latency/loss are the recorded scenario aggregates.", fontsize=8, color="#555555")
    fig.tight_layout(rect=(0.03, 0.06, 0.98, 0.92))
    pdf.savefig(fig)
    plt.close(fig)


def _training_page(pdf, run_dir):
    rewards_path = Path(run_dir) / "results" / "DDQN" / "rewards.csv"
    if not rewards_path.exists():
        _report_text_page(pdf, "DDQN training status", [("Training output", "DDQN reward history was not found. Training may have been interrupted or may not have started. No DDQN completion result is claimed.")], "Generated from this run folder's files.")
        return
    rewards = pd.to_numeric(pd.read_csv(rewards_path).iloc[:, 0], errors="coerce").dropna()
    fig, ax = plt.subplots(figsize=(11.7, 8.3))
    ax.plot(np.arange(1, len(rewards) + 1), rewards, color="#2878B5", marker="o", markersize=3)
    ax.set_title(f"DDQN training reward ({len(rewards)} recorded episodes)", fontsize=16)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Mean reward")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def generate_run_reports(run_dir, manifest=None, algorithm_errors=None, log_path=None):
    run_dir = Path(run_dir)
    manifest_path = run_dir / "experiment.json"
    if manifest is None and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = manifest or {}
    algorithm_errors = algorithm_errors or {}
    summary, _ = collect_algorithm_metrics(run_dir)
    summary_path = _write_comparison_csv(summary, run_dir)

    expected_ues = manifest.get("nUEs")
    expected_gnbs = manifest.get("nGnb")
    trace_count = len(list(run_dir.glob("[0-9]*/[0-9]*/traces.csv")))
    expected_traces = expected_ues * expected_gnbs if isinstance(expected_ues, int) and isinstance(expected_gnbs, int) else None
    present_algorithms = summary.loc[summary["Result status"] == "available", "Algorithm"].tolist()
    complete = len(present_algorithms) == len(ALGORITHM_DIRS) and not algorithm_errors and (expected_traces is None or trace_count == expected_traces)
    status = "COMPLETE" if complete else "PARTIAL / INCOMPLETE"

    run_log = Path(log_path) if log_path else run_dir / "run.log"
    if not run_log.exists():
        run_log = run_dir / "run.log"
    log_excerpt = []
    if run_log.exists():
        terms = ("Training the DQN", "DDQN training", "Training progress", "Scenario Score", "Completed algorithm", "Run status", "Final PDF report", "Algorithm performance PDF", "ERROR", "Traceback")
        log_excerpt = [line.rstrip() for line in run_log.read_text(encoding="utf-8", errors="replace").splitlines() if any(term in line for term in terms)][-12:]

    algorithm_lines = [f"{row['Algorithm']}: {row['Result status']}" for _, row in summary.iterrows()]
    config_lines = [f"{key}: {value}" for key, value in (manifest.get("parameters") or {}).items()]
    def fmt(value, suffix=""):
        try:
            number = float(value)
            return f"{number:.4g}{suffix}" if math.isfinite(number) else "n/a"
        except (TypeError, ValueError):
            return "n/a"
    metric_lines = []
    for _, row in summary.iterrows():
        metric_lines.append(
            f"{row['Algorithm']}: throughput {fmt(row.get('Mean throughput (Mbps)'), ' Mbps')}; "
            f"latency {fmt(row.get('Mean latency (ms)'), ' ms')}; "
            f"loss {fmt(row.get('Mean packet loss (%)'), '%')}; "
            f"handovers {fmt(row.get('Handover count'))}"
        )
    ascii_flow = """CONFIG + SCENARIO + WAYPOINTS
             |
             v
 ns-3 / 5G-LENA radio + UDP simulation
             |
             v
  UE/gNB trace CSV files (Time, RSRP, counters, latency)
             |
             v
 A3 | Rel.16 CHO | SBGH | ideal-SBGH | DDQN
             |
             v
 scenario.csv + scores + training history
             |
             v
 Final_Report.pdf + Algorithm_Performance.pdf"""
    report_path = run_dir / "Final_Report.pdf"
    with PdfPages(report_path) as pdf:
        _report_text_page(pdf, "HandoverLab 5G | Final Run Report", [
            ("Run status", f"{status}\nTrace files: {trace_count}" + (f" / {expected_traces} expected" if expected_traces is not None else "") + f"\nGenerated: {datetime.now().astimezone().isoformat(timespec='seconds')}"),
            ("Algorithm outputs", "\n".join(algorithm_lines) + ("\nAlgorithm errors: " + json.dumps(algorithm_errors, ensure_ascii=False) if algorithm_errors else "")),
            ("Metrics summarized from scenario CSVs", "\n".join(metric_lines)),
            ("Simulation flow", ascii_flow),
        ], f"Run folder: {run_dir}")
        _report_text_page(pdf, "Run configuration", [
            ("Effective parameters", "\n".join(config_lines) if config_lines else "No experiment manifest was available."),
            ("Input snapshots", str(manifest.get("input_snapshots", "Not recorded"))),
            ("Run log", str(run_log)),
        ], f"Run folder: {run_dir}")
        _report_text_page(pdf, "Run events, security, and interpretation", [
            ("Completion log events", "\n".join(log_excerpt) if log_excerpt else "No run log excerpt was available."),
            ("Security and privacy", "This is an offline ns-3 simulation, not a live IP measurement deployment. Handover policies do not detect measurement-as-DoS traffic or protect passive user contents. Trace files include location/signal/time fields that should be access-controlled. See the RFC-2330 security and privacy guide."),
            ("Interpretation limits", "No separate standardized reliability score, measured interruption duration, confidence interval, or multi-seed inference is computed. A handover count is not by itself a reliability metric; the configured latency penalty is not an observed interruption duration."),
        ], f"Run log: {run_log}")
        _bar_page(pdf, summary, "Algorithm performance comparison", [
            ("Mean throughput (Mbps)", "Mean throughput", "Mbps"),
            ("Mean latency (ms)", "Mean latency", "ms"),
            ("Handover count", "Handover count", "events"),
            ("Mean packet loss (%)", "Mean packet loss", "%"),
        ])
        _training_page(pdf, run_dir)

    comparison_path = run_dir / "Algorithm_Performance.pdf"
    with PdfPages(comparison_path) as pdf:
        _report_text_page(pdf, "HandoverLab 5G | Algorithm Performance", [
            ("Compared methods", "3GPP Rel.15 A3, 3GPP Rel.16 Conditional Handover, SBGH, ideal-SBGH, and DDQN."),
            ("Available results", "\n".join(algorithm_lines)),
            ("How to read this", "Throughput is averaged from the scenario.csv Throughput series and expressed in Mbps. Latency and PLostPackets are averaged from the same file. Handovers are summed where that column is present; a missing column is reported as unavailable. The summary values describe this run only."),
            ("Study caveats", "The source does not define a standalone interruption duration, a reliability score, confidence intervals, or statistical significance. Do not interpret fewer handovers as higher reliability without a separately stated metric."),
        ], f"Summary table: {summary_path.name}")
        _bar_page(pdf, summary, "Metrics from this run", [
            ("Mean throughput (Mbps)", "Mean throughput", "Mbps"),
            ("Mean latency (ms)", "Mean latency", "ms"),
            ("Handover count", "Handover count", "events"),
            ("Mean packet loss (%)", "Mean packet loss", "%"),
        ])

    status_path = run_dir / "run_status.json"
    status_path.write_text(json.dumps({
        "status": status,
        "trace_files": trace_count,
        "expected_trace_files": expected_traces,
        "algorithms_with_scenario_csv": present_algorithms,
        "algorithm_errors": algorithm_errors,
        "report": str(report_path),
        "performance_report": str(comparison_path),
    }, indent=2), encoding="utf-8")
    return {"report": report_path, "performance": comparison_path, "summary": summary_path, "status": status}
