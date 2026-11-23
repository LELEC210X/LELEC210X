#!/usr/bin/env python
#
# Copyright 2021 UCLouvain.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

"""
Per-Es/N0 performance summary and plots for packet_stats.

Deliberately free of any GNU Radio import so that it can be used offline.
"""

import numpy as np
import pandas as pd
from scipy import special

# Constant columns repeated on every row of the summary CSV so that the file
# is self-contained (theory curves and axes need them when re-plotting).


def compute_summary(
    df,
    isSimulation,
    payload_len,
    drate,
    fsamp,
    packets_per_esn0=0,
    EsN0_min=np.nan,
    EsN0_max=np.nan,
    n_EsN0=0,
    esn0_bin_width=1.0,
):
    """
    Reduce the per-packet dataframe to one row per Es/N0 value.

    Simulation mode
    ---------------
    Packets are grouped by their true Es/N0 (tagged by packet_generator).
    packets_per_esn0, EsN0_min, EsN0_max, and n_EsN0 describe the sweep
    and are used to compute missed-detection rates.

    Measurement mode (isSimulation=False)
    --------------------------------------
    The true Es/N0 is unknown; packets are clustered by estimated Es/N0
    (est_esn0_db) in bins of esn0_bin_width dB, and the row's esn0 value
    is the mean estimate of its bin. Sweep arguments are ignored and
    missed detections cannot be counted.

    Performance metrics per Es/N0 bin
    ----------------------------------
    - n_received / n_sent / n_missed : packet counts
    - miss_rate  : missed-detection rate  = 1 - n_received/n_sent
    - per        : packet error rate      = 1 - n_correct/n_received
    - ber        : bit error rate         = total_bit_errors / (n_received * n_bits_per_packet)
    - cfo_rmse_norm    : CFO RMSE normalised by the data rate
    - sto_rmse_symbols : STO RMSE in symbol units
    - est_esn0_mean    : mean of the receiver's Es/N0 estimate
    """
    payload_len = int(payload_len)

    if isSimulation:
        packets_per_esn0 = int(packets_per_esn0)
        grid = np.round(np.linspace(EsN0_min, EsN0_max, int(n_EsN0), endpoint=True), 6)

        df = df[df["true_esn0"].notna()].copy()
        df["true_esn0"] = df["true_esn0"].astype(float).round(6)
        key = "true_esn0"
        esn0 = np.union1d(grid, df["true_esn0"].unique())
    else:
        EsN0_min = EsN0_max = np.nan
        n_EsN0 = 0
        df = df[df["est_esn0_db"].notna()].copy()
        df["est_esn0_db"] = df["est_esn0_db"].astype(float)
        df = df[np.isfinite(df["est_esn0_db"])]
        # Bin each packet into a cluster index based on its estimated Es/N0
        df["esn0_cluster"] = np.floor(df["est_esn0_db"] / esn0_bin_width).astype(int)
        key = "esn0_cluster"
        # Cluster representative: mean estimated Es/N0 of its packets
        centers = df.groupby(key)["est_esn0_db"].mean().round(6)
        esn0 = centers.values
        df[key] = df[key].map(centers)
        EsN0_min = float(esn0.min()) if len(esn0) else np.nan
        EsN0_max = float(esn0.max()) if len(esn0) else np.nan
        n_EsN0 = len(esn0)

    grouped = df.groupby(key)
    s = pd.DataFrame(index=pd.Index(esn0, name="esn0"))

    # --- Packet counts per Es/N0 ---
    s["n_received"] = grouped.size().reindex(esn0).fillna(0).astype(int)
    s["n_correct"] = (
        grouped["crc_ok"]
        .apply(lambda g: int(g.fillna(False).astype(bool).sum()))
        .reindex(esn0)
        .fillna(0)
        .astype(int)
    )

    # Denominator: what was sent per Es/N0. Without it, fall back on what was
    # received (no missed-detection accounting).
    n_sent = (
        pd.Series(packets_per_esn0, index=esn0, dtype=float) if isSimulation else np.nan
    )
    s["n_sent"] = n_sent.astype(int) if isSimulation else np.nan
    s["n_missed"] = (
        (n_sent - s["n_received"]).clip(lower=0).astype(int) if isSimulation else np.nan
    )
    s["miss_rate"] = 1.0 - s["n_received"] / n_sent if isSimulation else np.nan

    # --- Packet Error Rate (PER) ---
    s["per"] = 1.0 - s["n_correct"] / s["n_received"]
    s.loc[s["n_received"] == 0, "per"] = 1.0

    # --- Bit Error Rate (BER) ---
    # BER: bit errors of received packets + 50 % errors on missed packets
    n_bits_pkt = payload_len * 8
    if df["n_bits"].notna().any():
        captured = grouped["bit_errors"].sum().reindex(esn0).fillna(0)
        s["bit_errors"] = captured
        s["ber"] = (captured) / (s["n_received"] * n_bits_pkt)
        s.loc[s["n_received"] == 0, "ber"] = 0.5
    else:
        s["bit_errors"] = np.nan
        s["ber"] = np.nan

    # --- Estimation error metrics (CFO RMSE, STO RMSE, mean SNR estimate) ---
    def _mean(col, fn=lambda x: x):
        if col not in df or not df[col].notna().any():
            return pd.Series(np.nan, index=esn0)
        return grouped[col].apply(lambda g: fn(g.dropna()).mean())

    s["cfo_rmse_norm"] = np.sqrt(_mean("cfo_error")) / drate
    s["sto_rmse_symbols"] = np.sqrt(_mean("sto_error"))  # * drate
    s["est_esn0_mean"] = _mean("est_esn0_db")
    s["est_sig_pow"] = _mean("est_sig_pow")

    # --- Metadata columns (self-contained for offline re-plotting) ---
    s["payload_len"] = payload_len
    s["drate"] = drate
    s["fsamp"] = fsamp
    s["packets_per_esn0"] = packets_per_esn0 if isSimulation else np.nan
    s["is_simulation"] = bool(isSimulation)

    s["esn0_bin_width"] = esn0_bin_width if not isSimulation else np.nan
    s["EsN0_min"] = EsN0_min if isSimulation else np.nan
    s["EsN0_max"] = EsN0_max if isSimulation else np.nan
    s["n_EsN0"] = int(n_EsN0) if isSimulation else np.nan

    return s.reset_index()


def _theory(esn0_db, payload_len):
    """
    Compute theoretical BER and PER curves for reference.

    Three standard AWGN bounds are computed:
      - Coherent FSK           : BER = 0.5 * erfc(sqrt(Es/N0 / 2))
      - Non-coherent FSK       : BER = 0.5 * exp(-Es/N0 / 2)
      - Coherent BPSK          : BER = 0.5 * erfc(sqrt(Es/N0))
    PER is derived from BER assuming independent bit errors:
      PER = 1 - (1 - BER)^(payload_len * 8)
    """
    esn0 = 10 ** (esn0_db / 10)
    n_bits = payload_len * 8
    ber = {
        "AWGN Th. FSK": 0.5 * special.erfc(np.sqrt(esn0 / 2)),
        "AWGN Th. FSK non-coh.": 0.5 * np.exp(-esn0 / 2),
        "AWGN Th. BPSK": 0.5 * special.erfc(np.sqrt(esn0)),
    }
    per = {k: 1 - (1 - v) ** n_bits for k, v in ber.items()}
    return ber, per


def plot_summary(
    summary,
    out_prefix=None,
    save_fig=False,
    logger=None,
    show=False,
    fig_array=None,
    ax_array=None,
    label=None,
    close=False,
    color=None,
):
    """
    Plot the Es/N0 curves of a summary dataframe, only for the data it holds.

    Curves can be superposed on existing plots: pass the (fig_array, ax_array)
    returned by a previous call (or by this one on another summary) to add the
    new curves to them instead of creating new figures. Panels are matched by
    name, so the result sets may hold different data; a panel that does not
    exist in the passed figures is skipped. Theory / reference curves are only
    drawn when a panel is created.

        figs, axs = plot_summary(summary_a, label="Run A")
        figs, axs = plot_summary(summary_b, label="Run B", fig_array=figs, ax_array=axs,
                                 save_fig=True, out_prefix="compare", show=True)

    Parameters
    ----------
    label : legend entry of this result (default "Measured" on the first one).
    close : close the figures once saved (when not shown). Leave False to keep
            using the returned figures; they are still valid when closed.

    Returns
    -------
    fig_array : dict {figure name: Figure}
    ax_array  : dict {figure name: {panel name: Axes}}
    Figure names: "esn0_vs_error_rate", "esn0_vs_estimators" (also the suffix
    of the saved PNGs). Panel names: "ber", "per", "cfo", "sto", "est_esn0",
    "miss_rate".

    """
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def log(msg):
        if logger is not None:
            logger.info(msg)
        else:
            print(msg)

    # Extract metadata from the first row (self-contained in the CSV)
    meta = summary.iloc[0]
    payload_len = int(meta["payload_len"])
    is_sim = bool(meta["is_simulation"]) if "is_simulation" in summary else True

    if is_sim:
        esn0_min, esn0_max = float(meta["EsN0_min"]), float(meta["EsN0_max"])
        grid = np.linspace(esn0_min, esn0_max, int(meta["n_EsN0"]), endpoint=True)
    else:
        # Measurement: no sweep, use the range of estimated Es/N0 (axes and theory curves)
        esn0_min, esn0_max = float(summary["esn0"].min()), float(summary["esn0"].max())
        grid = np.linspace(esn0_min - 1, esn0_max + 1, 100)

    ber_th, per_th = _theory(grid, payload_len)
    th_styles = ["--", "-.", ":"]

    x = summary["esn0"]
    meas_label = label if label is not None else "Measured"

    fig_array = {} if fig_array is None else fig_array
    ax_array = {} if ax_array is None else ax_array

    def get_figure(fig_name, panels, width):
        """Return existing (fig, {panel: ax}, False) or a new one with the panels holding data."""
        if fig_name in fig_array and fig_name in ax_array:
            return fig_array[fig_name], ax_array[fig_name], False
        names = [name for name, has_data in panels if has_data]
        if not names:
            return None, {}, False
        fig, axes = plt.subplots(
            1, len(names), figsize=(width * len(names), 4), squeeze=False
        )
        fig_array[fig_name] = fig
        ax_array[fig_name] = dict(zip(names, axes[0]))
        return fig, ax_array[fig_name], True

    def extend_xlim(ax, lo, hi):
        cur_lo, cur_hi = ax.get_xlim()
        ax.set_xlim((min(cur_lo, lo), max(cur_hi, hi)))

    def finish(fig, fig_name, axes):
        # A single legend per figure, below the subplots: gather the distinct
        # entries of all the panels (the same label on several panels is shown once).
        entries = {}
        for ax in axes.values():
            for handle, lab in zip(*ax.get_legend_handles_labels()):
                entries.setdefault(lab, handle)
        for old_legend in list(fig.legends):
            old_legend.remove()
        fig.tight_layout()
        if entries:
            legend = fig.legend(
                list(entries.values()),
                list(entries.keys()),
                loc="lower center",
                bbox_to_anchor=(0.5, 0),
                frameon=False,
                ncol=min(len(entries), 4, max(1, int(fig.get_figwidth() // 2))),
            )
            # Reserve room for the legend at the bottom of the figure
            fig.canvas.draw()
            height = (
                legend.get_window_extent()
                .transformed(fig.transFigure.inverted())
                .height
            )
            fig.tight_layout(rect=(0, height, 1, 1))
        if save_fig:
            path = f"{out_prefix}_{fig_name}.png"
            fig.savefig(path)
            log(f"Saved {path}")
        if close and not show:
            plt.close(fig)

    def curve(
        axes,
        name,
        y,
        new,
        xlabel_ylabel_title,
        yscale=None,
        ylim=None,
        xlim=True,
        marker="o",
        theory=None,
        color=color,
        **plot_kw,
    ):
        """Add the measured curve y to panel `name` (if it exists), set up the panel if new."""
        ax = axes.get(name)
        if ax is None or not y.notna().any():
            return
        if yscale == "log":
            ax.semilogy(x, y, marker=marker, label=meas_label, color=color, **plot_kw)
        else:
            ax.plot(x, y, marker=marker, label=meas_label, color=color, **plot_kw)
        if new:
            for (th_name, th_curve), ls in zip((theory or {}).items(), th_styles * 2):
                ax.plot(grid, th_curve, ls, color="gray", label=th_name)
            xlabel, ylabel, title = xlabel_ylabel_title
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_title(title)
            ax.grid(True, which="both")
            if yscale:
                ax.set_yscale(yscale)
            if ylim:
                ax.set_ylim(ylim)
            if xlim:
                ax.set_xlim((esn0_min, esn0_max + 1))
        elif xlim:
            extend_xlim(ax, esn0_min, esn0_max + 1)

    esn0_label = "$E_{s}/N_{0}$ [dB]"

    # -------------------------------------------------------------------------
    # Figure 1: BER and PER vs Es/N0
    # -------------------------------------------------------------------------
    fig_name = "esn0_vs_error_rate"
    fig, axes, new = get_figure(
        fig_name,
        [("ber", summary["ber"].notna().any()), ("per", summary["per"].notna().any())],
        4,
    )
    if fig is not None:
        curve(
            axes,
            "ber",
            summary["ber"],
            new,
            (esn0_label, "BER", "SNR vs BER"),
            yscale="log",
            ylim=(1e-6, 1),
            xlim=False,
            theory=ber_th,
        )
        curve(
            axes,
            "per",
            summary["per"],
            new,
            (esn0_label, "PER", "SNR vs PER error"),
            yscale="log",
            ylim=(1e-6, 1),
            theory=per_th,
        )
        finish(fig, fig_name, axes)

    # -------------------------------------------------------------------------
    # Figure 2: CFO/STO estimation error, estimated SNR, and missed-detection rate
    # -------------------------------------------------------------------------
    fig_name = "esn0_vs_estimators"
    fig, axes, new = get_figure(
        fig_name,
        [
            ("cfo", summary["cfo_rmse_norm"].notna().any()),
            ("sto", summary["sto_rmse_symbols"].notna().any()),
            ("est_esn0", summary["est_esn0_mean"].notna().any()),
            ("miss_rate", summary["miss_rate"].notna().any()),
        ],
        2.5,
    )
    if fig is not None and (summary["is_simulation"][0] == 1):
        curve(
            axes,
            "cfo",
            summary["cfo_rmse_norm"],
            new,
            (esn0_label, "CFO RMSE / data rate", "CFO Estimation"),
            yscale="log",
        )
        curve(
            axes,
            "sto",
            summary["sto_rmse_symbols"],
            new,
            (esn0_label, "STO RMSE (symbols)", "STO Estimation"),
            yscale="log",
        )
        curve(
            axes,
            "est_esn0",
            summary["est_esn0_mean"],
            new,
            (esn0_label, "Estimated $E_{s}/N_{0}$", "Estimated SNR"),
            xlim=False,
            marker=".",
        )
        curve(
            axes,
            "miss_rate",
            summary["miss_rate"],
            new,
            (esn0_label, "Missed detection rate", "Missed detection"),
            ylim=(-0.05, 1.05),
            xlim=False,
        )
        # Overlay the ideal "estimated = true" diagonal for the SNR estimator panel
        if new and is_sim and "est_esn0" in axes:
            axes["est_esn0"].plot(x, x, "--", color="black", label="Ideal")
        finish(fig, fig_name, axes)

    if show:
        plt.show()

    return fig_array, ax_array


def plot_cfo_histogram(
    df, out_prefix=None, save_fig=False, logger=None, show=False, bins=20, close=False
):
    """
    Plot a histogram of the estimated CFO (est_cfo column) from a per-packet dataframe.

    Parameters
    ----------
    df         : per-packet DataFrame (or any object with an "est_cfo" column).
    out_prefix : path prefix for the saved PNG (<out_prefix>_cfo_histogram.png).
    save_fig   : write the PNG to disk when True.
    logger     : optional logger; falls back to print().
    show       : call plt.show() after plotting.
    bins       : number of histogram bins (default 20).
    close      : close the figure after saving (useful in long-running GR flows).

    Returns
    -------
    fig : the matplotlib Figure, or None if no est_cfo data is present.

    """
    import matplotlib

    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def log(msg):
        if logger is not None:
            logger.info(msg)
        else:
            print(msg)

    cfo = df["est_cfo"].dropna() if "est_cfo" in df else pd.Series([], dtype=float)
    if cfo.empty:
        log("[STATS] No est_cfo values — skipping CFO histogram.")
        return None

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(cfo, bins=bins, color="tab:blue", edgecolor="white", linewidth=1)
    ax.set_xlabel("Estimated CFO [Hz]")
    ax.set_ylabel("Number of packets")
    ax.set_title(f"Estimated CFO ({len(cfo)} packets)")
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_axisbelow(True)
    fig.tight_layout()

    if save_fig:
        path = f"{out_prefix}_cfo_histogram.png"
        fig.savefig(path)
        log(f"Saved {path}")

    if show:
        plt.show()

    if close and not show:
        plt.close(fig)

    return fig
