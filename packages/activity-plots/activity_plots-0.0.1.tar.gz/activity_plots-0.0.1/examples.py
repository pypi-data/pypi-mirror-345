import argparse
import numpy as np
import matplotlib.pyplot as plt
import activity_plots

# [Optional] Import seaborn for styling
import seaborn as sns

sns.set_theme(style="whitegrid")

np.random.seed(0)


def multi_bar_segments():
    # Build data container of random segments
    N, C = 10, 4
    starts = np.random.randint(0, 100, N)
    data = activity_plots.ActivitySegments(
        starts=starts,
        ends=starts + np.random.randint(1, 20, N),
        label_ids=np.random.randint(0, C, N),
        label_set=[f"Class {x}" for x in range(C)],
    )
    print(data.df)

    # Plot
    _, ax = plt.subplots(figsize=(10, 3), layout="constrained")
    ax = activity_plots.multi_bar(ax, data, title="multi_bar example", xlabel="Frame/Time")
    plt.savefig("images/multi_bar_segments.png")
    # plt.show()  # Uncomment to show


def multi_bar_sequence():
    data = activity_plots.segments_from_sequence(
        [1, 1, 1, 0, 0, 0, 2, 2, 3, 3, 3, 4, -1, -1, 5, 5, 2, 2, 2, 2],
        label_set=[f"Class {x}" for x in range(8)],
    )
    print(data.df)
    _, ax = plt.subplots()
    ax = activity_plots.multi_bar(ax, data)
    plt.savefig("images/multi_bar_sequence.png")


def single_bar():
    # Build list for plot
    all_data = []
    y_labels = []
    label_set = [f"Class {x}" for x in range(8)]
    for i in range(1, 6):
        rand_labels = np.random.randint(-1, 8, 20)
        rand_lengths = np.random.randint(1, 10, 20)
        rand_seq = np.concatenate([np.repeat(a, b) for a, b in zip(rand_labels, rand_lengths)])
        data = activity_plots.segments_from_sequence(rand_seq, label_set)
        all_data.append(data)
        y_labels.append(f"Video {i}")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 3), layout="constrained")
    ax = activity_plots.single_bar(
        ax,
        all_data=all_data,
        ylabels=y_labels,
        title="single_bar example",
    )
    plt.savefig("images/single_bar.png")


def continuous_shaded():
    # Build array of random probabilities
    data = np.random.rand(50, 8) / 20.0
    data[10:45, 0] = np.linspace(0.25, 0.99, 35)
    data[10:45, 1] = np.linspace(0.9, 0.1, 35)
    data[25:50, 3] = np.random.rand(25)
    # data[:, 4] = -10.0
    data[:, 5] = 0.0
    data[:, 6] = 0.9
    data[:, 7] = 1.0

    # Create data container
    label_set = [f"Class {x}" for x in range(8)]
    act_probs = activity_plots.ActivityProbabilities(data, label_set)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 3), layout="constrained")
    ax = activity_plots.continuous_shaded(
        fig=fig,
        ax=ax,
        data=act_probs,
        title="continuous_shaded example",
        xlabel="Frame/Time",
    )
    plt.savefig("images/continuous_shaded.png")


def main():
    multi_bar_segments()
    multi_bar_sequence()
    single_bar()
    continuous_shaded()


if __name__ == "__main__":
    main()
