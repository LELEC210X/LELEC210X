#!/usr/bin/env python
"""
Superpose the Es/N0 curves of several packet_stats summaries (simulations and
tests). Edit the SUMMARIES dictionary below to set which summaries to plot.

    python plot_summaries.py
    python plot_summaries.py --out-prefix export/compare --show

Paths in SUMMARIES are relative to this script's directory, so the script can
be run from anywhere.

Saves <out-prefix>_esn0_vs_error_rate.png and <out-prefix>_esn0_vs_estimators.png
(default prefix: this script's directory / "summaries").

Simulations are plotted before tests, whatever their order in SUMMARIES,
because the first summary plotted sets up the panels and tests lack some of
them (e.g. BER). Each summary keeps the color of its position in SUMMARIES.

Needs only numpy, scipy, pandas and matplotlib (no GNU Radio).
"""

# ── Edit this dictionary to change which summaries are plotted ────────────────
# Keys   : legend labels shown in the figures
# Values : paths relative to this script's directory (apps/)
SUMMARIES = {
    "Test": "export/gnu_output.csv",
}
# ─────────────────────────────────────────────────────────────────────────────

import argparse
import importlib.util
import os
import sys

import pandas as pd

# Base directory = directory containing this script, regardless of cwd
_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_stats_plots():
    """Use the repo copy of stats_plots.py (no gnuradio import), else the installed one."""
    path = os.path.join(_HERE, "..", "python", "stats_plots.py")
    if os.path.isfile(path):
        spec = importlib.util.spec_from_file_location("stats_plots", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    from LELEC210X import stats_plots

    return stats_plots


def _resolve_entries():
    """Return [(absolute path, label)] from SUMMARIES, aborting on missing files."""
    entries = []
    for label, rel_path in SUMMARIES.items():
        abs_path = os.path.join(_HERE, rel_path)
        if not os.path.isfile(abs_path):
            sys.exit(f"Summary not found: {abs_path}  (from SUMMARIES['{label}'])")
        entries.append((abs_path, label))
    if not entries:
        sys.exit("SUMMARIES is empty — add at least one entry.")
    return entries


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--out-prefix",
        help="prefix of the saved PNGs (default: <script dir>/summaries)",
    )
    parser.add_argument(
        "--show", action="store_true", help="also open the figures interactively"
    )
    args = parser.parse_args()

    prefix = args.out_prefix or os.path.join(_HERE, "summaries")

    # Color set by the position in SUMMARIES: the same on every panel, even
    # those that do not hold all the summaries.
    results = [
        {"summary": pd.read_csv(path), "label": label, "color": f"C{index}"}
        for index, (path, label) in enumerate(_resolve_entries())
    ]
    results.sort(
        key=lambda result: not bool(result["summary"]["is_simulation"].iloc[0])
    )

    stats_module = _load_stats_plots()

    if args.show:
        # plot_summary(show=True) calls plt.show() each time: do not block before the last summary
        import matplotlib.pyplot as plt

        plt.ion()

    fig_array, ax_array = None, None
    for result in results:
        fig_array, ax_array = stats_module.plot_summary(
            result["summary"],
            label=result["label"],
            color=result["color"],
            show=args.show,
            fig_array=fig_array,
            ax_array=ax_array,
        )

    import matplotlib.pyplot as plt

    # Saved here, not by plot_summary: it does not save the estimators figure on a test summary
    for fig_name, fig in fig_array.items():
        if not any(ax.has_data() for ax in ax_array[fig_name].values()):
            plt.close(fig)  # e.g. estimators figure when SUMMARIES only lists tests
            continue
        out_path = f"{prefix}_{fig_name}.png"
        fig.savefig(out_path)
        print(f"Saved {out_path}")

    if args.show:
        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()
