# Learning Path

The goal is to learn robotics while building demos that are useful at work.

## Stage 1: ROS 2 Data Flow

Concepts:

- nodes
- topics
- messages
- services
- actions
- launch files
- parameters

Practice:

- list topics,
- echo messages,
- publish a velocity command,
- inspect message definitions,
- launch a small node from this repo.

## Stage 2: Robot Motion

Concepts:

- differential drive motion,
- linear velocity,
- angular velocity,
- odometry,
- dead reckoning,
- command limits.

Practice:

- drive forward slowly,
- rotate in place,
- compare commanded motion with odometry,
- understand drift.

## Stage 3: Sensors

Concepts:

- LiDAR scans,
- camera images,
- sensor frames,
- update rates,
- noise,
- bandwidth.

Practice:

- visualize `/scan`,
- move objects around the robot,
- inspect camera frame rate and latency.

## Stage 4: Transforms

Concepts:

- `map`,
- `odom`,
- `base_link`,
- `laser`,
- static transforms,
- dynamic transforms.

Practice:

- generate a TF tree,
- fix missing sensor transforms,
- verify laser data aligns with the robot in RViz.

## Stage 5: Mapping and Localization

Concepts:

- occupancy grid,
- SLAM,
- localization,
- pose estimate,
- map saving.

Practice:

- map a room,
- save the map,
- restart and localize on the saved map.

## Stage 6: Navigation

Concepts:

- Nav2,
- behavior tree,
- global planner,
- local controller,
- costmaps,
- recovery behaviors,
- navigation actions.

Practice:

- send one goal,
- send multiple waypoints,
- log success, failure, pause, and recovery events.

## Stage 7: Platform Testing

Concepts:

- robot health,
- mission state,
- observability,
- teleoperation,
- event capture,
- incident review,
- fleet metadata.

Practice:

- expose battery, CPU, mission state, pose, scan, image, and anomalies,
- trigger synthetic navigation anomalies,
- record the relevant time window.

## Stage 8: AI Layer

Concepts:

- natural-language command parsing,
- guarded robot actions,
- narration,
- retrieval from maps and mission logs,
- human override.

Practice:

- accept text command: "start the room tour",
- convert it into a waypoint mission,
- explain robot state in plain language.
