# activity-plots

Plotting tools for temporal action localization (or per-frame classification) labels and predictions.

# Install

```bash
pip install activity-plots
```

# Usage

Create a data container then pass it into one of the plotting functions.

```python
import activity_plots
import matplotlib.pyplot as plt

data = activity_plots.ActivitySegments(
    starts=[5, 13, 29], ends=[15, 17, 45], label_ids=[0, 1, 0],
    label_set=["Activity A", "Activity B"]
)
fig, ax = plt.subplots()
ax = activity_plots.multi_bar(ax, data, title="Test Plot", xlabel="Frame #")
plt.show()
```


# Plot Types

1. `multi_bar`

![Example plot](/images/multi_bar_segments.png)

2. `continuous_shaded` 
    - Use to visualize probabilities (model output)

![Example plot](/images/continuous_shaded.png)

3. `single_bar` 
    - Use when there can only be one label per frame
    - Useful to visualize multiple videos/instances

![Example plot](/images/single_bar.png)

# Data Containers

`ActivitySegments`
- Build from a set of variable-length segments

`ActivityProbabilities`
- Used for visualizing predictions (per-frame distributions over all activities)

`segments_from_sequence` 
- Helper function to build ActivitySegments from a sequence of label IDs.
- Example:
```python
seq = [1, 1, 1, 0, 2, 3, 3, 3, 4, -1, -1, 5]  # -1 is ignored ("background")
data = activity_plots.segments_from_sequence(seq)
```

# TODO

- [ ] Github action to publish on pypi
- [ ] Stackplot
    - Check different options for "baseline"
- [ ] Ridge plot
    - Fill color with same colormap as multi-bar
- [ ] Better handling of overlapping segments
    - Could use  additional offset
    - Might need to increase the y-axis range too
- [ ] Create tests