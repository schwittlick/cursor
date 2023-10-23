Notes
-----

Length, how many points
![all_length.png](all_length.png)

Distance normalized absolute
![all_distance_absolute.png](all_distance_absolute.png)

Distance normalized relative (divided by length)
![all_distance_relative.png](all_distance_relative.png)

Duration in s (discarded all above 30s)
![all_duration_in_s.png](all_duration_in_s.png)

Measurements
------------

Entropy X
![all_entropy_x.png](all_entropy_x.png)

Differential Entropy X
![all_differential_entropy_x.png](all_differential_entropy_x.png)

Entropy Y
![all_entropy_y.png](all_entropy_y.png)

Differential Entropy Y
![all_differential_entropy_y.png](all_differential_entropy_y.png)

Entropy Direction Change
![all_entropy_direction_change.png](all_entropy_direction_change.png)

Variation X
![all_variation_x.png](all_variation_x.png)

Variation Y
![all_variation_y.png](all_variation_y.png)

About 2% of all paths are 1-dimensional either in x- or y-dimension

    This is how long it takes to load everythin file-by-file
    ℹ Loaded 310224 paths from 116 recordings
    ℹ Loaded 0 keys from 116 recordings
    ℹ This took 76202ms.

    Pickled:
    INFO: Loading 2023.pckl took : 59100ms

When doing direction change entropy calculation, all paths with only 2 vertices are 0

length:

- 2000 paths (1%) are longer than 600 vertices

differential entropy:

- x: INFO: Total 264568 paths // possible to compute (15% impossible. because too few points or -inf entropy)
- y: INFO: Total 227199 paths // 17%

Potential todo

- drop 1-dimensional paths
- export pickles of certain entropy buckets
- drop paths with less than 3 vertices