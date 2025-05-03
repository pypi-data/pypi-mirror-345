import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import colormaps as cmaps

from activity_plots import ActivitySegments, ActivityProbabilities


def multi_bar(
    ax: plt.Axes,
    data: ActivitySegments,
    title: str = "",
    xlabel: str = "Frame #",
    param_dict: dict = {},
):
    num_labels = len(data.label_set)

    # Warn on too many labels
    if num_labels > 50:
        warnings.warn("More than 50 labels - might want to consider a different plot type.")

    # Create bars for each segment
    colors = cmaps.cet_g_hv
    for label_id, subdf in data.df.groupby("label_id"):
        out = ax.broken_barh(
            xranges=subdf[["start", "length"]].values,
            yrange=(label_id - 0.4, 0.8),
            edgecolor="black",
            alpha=0.7,
            linewidth=1,
            facecolor=colors(label_id),
            **param_dict,
        )

    # Set y-axis ticks to label names
    ax.set_yticks(
        ticks=np.arange(num_labels),
        labels=data.label_set,
        rotation=0,
        fontdict={"multialignment": "center"},
    )

    # Set chart elements
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_xlim(-1, data.total_length + 1)
    ax.set_ylim(-0.5, num_labels - 0.5)
    ax.invert_yaxis()
    return out


def single_bar(
    ax: plt.Axes,
    all_data: list[ActivitySegments],
    ylabels: list[str],
    title: str = "",
    xlabel: str = "Frame #",
    include_legend: bool = True,
    param_dict: dict = {},
):
    num_rows = len(all_data)

    # Create bars for each segment
    colors = cmaps.cet_g_hv
    for i, data in enumerate(all_data):
        ax.barh(
            y=ylabels[i],
            width=data.df["length"].values,
            alpha=0.7,
            height=0.8,
            linewidth=0,
            left=data.df["start"].values,
            label=data.df["label_name"].values,
            color=colors(data.df["label_id"].values),
            **param_dict,
        )

    # Add legend outside plot
    labels = all_data[0].label_set
    patches = [mpatches.Patch(color=colors(i), label=l) for i, l in enumerate(labels)]
    ax.legend(
        handles=patches,
        bbox_to_anchor=(1, 1),
        loc="upper left",
        fontsize="small",
    )

    # Set chart elements
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_xlim(-1, None)
    ax.set_yticks(np.arange(num_rows), ylabels)
    ax.invert_yaxis()
    return ax


def continuous_shaded(
    fig: plt.Figure,
    ax: plt.Axes,
    data: ActivityProbabilities,
    title: str = "",
    xlabel: str = "Frame #",
    param_dict: dict = {},
):
    # Plot with pcolormesh
    out = ax.pcolormesh(
        data.probs.T,
        shading="nearest",
        vmin=min(0, data.probs.min()),
        vmax=max(1, data.probs.max()),
        cmap="Blues",
        **param_dict,
    )

    # Add colorbar
    fig.colorbar(out, ax=ax)

    # Set y-axis ticks to label names
    ax.set_yticks(
        ticks=np.arange(len(data.label_set)),
        labels=data.label_set,
        rotation=0,
        fontdict={"multialignment": "center"},
    )

    # Set chart elements
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.invert_yaxis()
    return out
