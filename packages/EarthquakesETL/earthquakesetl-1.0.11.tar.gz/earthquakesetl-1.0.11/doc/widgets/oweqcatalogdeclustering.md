EQ Catalog Declustering
===========


Declustering is a process in seismology used to separate dependent events, such as foreshocks
and aftershocks, from independent mainshock events within an earthquake catalog. This separation
is crucial for accurate seismic hazard assessments, as it ensures that the analysis focuses on
independent seismic events rather than clusters of related events.

Gardner-Knopoff Declustering Method
-------

The Gardner-Knopoff method identifies and removes aftershocks based on predefined time and
spatial windows that are dependent on the magnitude of the mainshock.

**Parameters**:

- *fs_time_prop*: This parameter represents the fraction of the time window used for aftershocks. It is a value between 0 and 1 that adjusts the duration considered for aftershock identification.

- *time_distance_window*: This object calculates the time and distance windows for each event based on its magnitude. It is essential for determining the temporal and spatial range within which other events can be classified as aftershocks.

Adjusting these parameters influences the number of events classified as aftershocks. A larger
time window or higher fs_time_prop may result in more events being identified as aftershocks,
thereby reducing the number of events classified as mainshocks.


Nearest Neighbor Declustering Method
-----------

The Nearest Neighbor method analyzes the spatial and temporal distances between events to
distinguish between clustered events (foreshocks and aftershocks) and background seismicity.

**Parameters**:

- *q_value*: This parameter controls the temporal sensitivity of the algorithm to clustered events. It is used to scale the time window based on the magnitude of the event, giving more weight to events that are closer in time.
  - A higher q_value reduces the effective time window for larger magnitudes, making temporally close events less likely to form a cluster.
- *b_value*: This parameter is part of the Gutenberg-Richter law and describes the relationship between earthquake magnitude and frequency. In this method, b_value adjusts how magnitude influences both temporal and spatial distances.
  - A higher b_value reduces the weight of smaller magnitude earthquakes, favoring their classification as independent events.
- *fractal_dimension*: This parameter describes the spatial complexity of the earthquake distribution. It affects how the spatial window is calculated to evaluate whether an event is part of a cluster.
  - A higher fractal_dimension amplifies the influence of spatial distances between events, making event clustering more restrictive.