# Autonomous Tour Guide

Create 3 + Raspberry Pi 4B + RPLIDAR A1 + Raspberry Pi Camera demo workspace.

The first demo target is a room tour robot:

1. scan and map a room,
2. localize on that map,
3. navigate through named waypoints,
4. publish mission, health, and anomaly signals that robotics platforms can monitor,
5. later add an AI layer for natural-language commands and narration.

## Hardware

- iRobot Create 3, connected on the same network as the Raspberry Pi
- Raspberry Pi 4B running Ubuntu 22.04 and ROS 2 Humble
- SLAMTEC RPLIDAR A1
- Raspberry Pi Camera

## Repository Layout

- `src/autonomous_tour_guide`: ROS 2 Python package for demo orchestration.
- `docs/bringup_checklist.md`: step-by-step hardware and ROS checks.
- `docs/learning_path.md`: robotics concepts to learn while building the demo.
- `docs/platform_demo_strategy.md`: why this demo is useful for platform testing.
- `scripts`: helper shell scripts for repeatable checks.

## First Milestone

The first milestone is not full autonomy. It is reliable visibility:

- Create 3 publishes odometry, battery, robot state, and command velocity.
- RPLIDAR publishes `sensor_msgs/LaserScan`.
- Camera publishes an image stream.
- RViz can show robot frames, laser scan, odometry, map, and navigation goals.
- The demo package publishes a simple mission state topic.

That gives us enough signal to test observability, alerts, recordings, incident review, and mission tracking platforms.

## Build

From the repo root:

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

The default camera and teleop launch files use existing ROS 2 packages:

```bash
sudo apt install ros-humble-camera-ros ros-humble-v4l2-camera ros-humble-teleop-twist-keyboard
```

For compressed image topics, also install:

```bash
sudo apt install ros-humble-image-transport-plugins
```

## Run the Local Demo Nodes

```bash
ros2 launch autonomous_tour_guide observability_demo.launch.py
```

This starts the demo status publisher. It is intentionally small: it gives us a stable topic contract before we connect platform agents or navigation.

Once Nav2 is running and localized on a map:

```bash
ros2 launch autonomous_tour_guide waypoint_tour.launch.py
```

This sends the robot through the configured waypoints in `src/autonomous_tour_guide/config/waypoints.yaml`.

## Camera Streaming

For a Raspberry Pi camera using the normal libcamera stack:

```bash
ros2 launch autonomous_tour_guide camera_stream.launch.py
```

Useful overrides:

```bash
ros2 launch autonomous_tour_guide camera_stream.launch.py \
  video_device:=/dev/video0 image_width:=640 image_height:=480 frame_rate:=15
```

The launch publishes `/camera/image_raw` and `/camera/camera_info` by default.

For a USB camera or a camera exposed as a working V4L2 device:

```bash
ros2 launch autonomous_tour_guide camera_stream.launch.py camera_backend:=v4l2 video_device:=/dev/video0
```

## Manual Robot Control

Put the robot on the floor with clearance, then run:

```bash
ros2 launch autonomous_tour_guide manual_control.launch.py
```

This starts `teleop_twist_keyboard` on `/tour_guide/manual_cmd_vel` and a safety filter that limits speed and republishes to `/cmd_vel`. If the Create 3 command topic is namespaced, pass it explicitly:

```bash
ros2 launch autonomous_tour_guide manual_control.launch.py cmd_vel_topic:=/pada_1/cmd_vel
```

## Basic Bringup

Camera streaming and demo status can be started together:

```bash
ros2 launch autonomous_tour_guide robot_bringup.launch.py
```

Manual control is opt-in from the combined launch:

```bash
ros2 launch autonomous_tour_guide robot_bringup.launch.py start_manual_control:=true
```
