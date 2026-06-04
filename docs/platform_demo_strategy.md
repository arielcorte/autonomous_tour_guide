# Platform Demo Strategy

The first tour-guide demo should be useful for robotics platform testing, not only robot motion.

## What The Platforms Care About

Formant emphasizes fleet observability, device configuration, multi-device video, teleoperation, and telemetry dashboards.

InOrbit focuses on robot operations, missions, navigation dashboards, teleoperation, relocalization, APIs, and operational metrics.

Insaion emphasizes ROS 2 observability, host metrics, topic monitoring, edge-local recordings, MCAP support, alarms, incident history, and AI diagnostics.

Heex focuses on smart data: event-triggered capture, edge or server deployment, relevant data windows, tags, and scenario-driven recordings.

## Demo Shape

Build the robot as a small autonomous mission system:

```text
Start mission -> navigate to waypoint A -> narrate -> waypoint B -> narrate -> waypoint C -> return home
```

At every step, publish:

- mission id,
- mission state,
- current waypoint,
- battery percentage,
- robot pose,
- navigation result,
- anomaly flags,
- short human-readable status.

This gives every platform a useful integration surface:

- dashboards can show state and metrics,
- mission systems can track progress,
- teleoperation can take over when blocked,
- recording systems can capture only failure windows,
- AI diagnostics can correlate robot, sensor, and host signals.

## First Client-Visible Scenario

Use a small room with three labeled stops:

- `home`
- `station_1`
- `station_2`
- `station_3`

The robot:

1. starts at home,
2. announces mission start,
3. drives to each station,
4. pauses and publishes a tour message,
5. reports success or failure,
6. returns home.

## Useful Failure Cases

Do not hide failures. Good platform demos need controlled incidents.

- obstacle blocks the path,
- battery is low,
- LiDAR scan disappears,
- camera stream drops,
- localization confidence is poor,
- robot is manually moved during the mission.

Each failure should produce a clear event. That is what observability platforms are built to show.
