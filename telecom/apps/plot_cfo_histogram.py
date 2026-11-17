#!/usr/bin/env python
"""
Plot the histogram of the estimated CFO (est_cfo field) of the packets of a
per-packet trace written by the packet_stats block.

    python plot_cfo_histogram.py
    python plot_cfo_histogram.py --trace_csv export/gnu_output_trace.csv --bins 40 --show

The default trace path is export/gnu_output_trace.csv relative to this script.
Saves <trace path without extension>_cfo_histogram.png by default.

Needs only pandas and matplotlib (no GNU Radio).
"""

import argparse
import importlib.util
import os
import sys

import pandas as pd

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


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trace_csv", default=os.path.join(_HERE, "export/gnu_output_trace.csv"),
                        help="per-packet trace CSV written by packet_stats (default: export/gnu_output_trace.csv)")
    parser.add_argument("--bins", type=int, default=20, help="number of histogram bins (default: 20)")
    parser.add_argument("--out", help="path of the saved PNG. Not saved if not specified")
    parser.add_argument("--show", action="store_true", help="also open the figure interactively")
    args = parser.parse_args()

    if not os.path.isfile(args.trace_csv):
        sys.exit(f"Trace not found: {args.trace_csv}")
    trace = pd.read_csv(args.trace_csv)
    if "est_cfo" not in trace or not trace["est_cfo"].notna().any():
        sys.exit(f"{args.trace_csv}: no est_cfo values (is it a per-packet trace?)")

    # plot_cfo_histogram saves to <out_prefix>_cfo_histogram.png, so strip
    # that suffix from --out if the user passed a full filename, otherwise
    # derive the prefix from the trace path.
    out_prefix = None
    if args.out:
        suffix = "_cfo_histogram.png"
        out_prefix = args.out[:-len(suffix)] if args.out.endswith(suffix) else os.path.splitext(args.out)[0]


    _load_stats_plots().plot_cfo_histogram(
        trace, out_prefix=out_prefix, save_fig=args.out is not None, show=args.show, bins=args.bins)


if __name__ == "__main__":
    main()
