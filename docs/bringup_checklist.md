# Bring-up Checklist

This is the order we should use on the physical robot. Each step proves one layer before relying on the next one.

## 1. ROS Environment

On the Raspberry Pi:

```bash
source /opt/ros/humble/setup.bash
ros2 doctor --report
printenv ROS_DOMAIN_ID
```

Learning point: ROS 2 nodes discover each other through DDS. If machines cannot discover each other, topics will appear missing even when code is correct.

## 2. Create 3 Discovery

On the Raspberry Pi:

```bash
ros2 topic list
ros2 node list
```

Expected signs:

- Create 3 topics are visible.
- You can see odometry, battery, and robot state topics.

If nothing appears, check:

- Pi and Create 3 are on the same network.
- `ROS_DOMAIN_ID` matches on all ROS machines.
- multicast is allowed on the network.

## 2a. Distrobox Discovery

If the Raspberry Pi can see Create 3 topics but the distrobox cannot, first prove the container environment:

```bash
distrobox enter ros2-humble -- bash -ic '
  echo ROS_DISTRO=${ROS_DISTRO:-unset}
  echo ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-unset}
  echo RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-unset}
  echo ROS_LOCALHOST_ONLY=${ROS_LOCALHOST_ONLY:-unset}
  ros2 topic list -t | rg "pada_1|irobot_create_msgs|battery_state|cmd_vel"
'
```

Expected for the current setup:

- `ROS_DISTRO=humble`
- `ROS_DOMAIN_ID=0`
- `ROS_LOCALHOST_ONLY=0` or unset
- Create 3 topics under `/pada_1/...`

Important distrobox details:

- An interactive shell loads `.bashrc`; non-interactive commands may not. If using `bash -lc`, explicitly run `source /opt/ros/humble/setup.bash` first.
- The container should use host networking for normal DDS multicast discovery:

```bash
podman inspect ros2-humble --format '{{.HostConfig.NetworkMode}}'
```

Expected output:

```text
host
```

If the environment is correct but topics still do not appear, restart the ROS daemon inside the distrobox:

```bash
distrobox enter ros2-humble -- bash -ic '
  ros2 daemon stop
  ros2 daemon start
  ros2 topic list -t
'
```

## 3. Create 3 Motion Safety

Put the robot on the floor with space around it.

For guarded keyboard control:

```bash
ros2 launch autonomous_tour_guide manual_control.launch.py
```

If the Create 3 uses a namespace:

```bash
ros2 launch autonomous_tour_guide manual_control.launch.py cmd_vel_topic:=/pada_1/cmd_vel
```

The launch routes keyboard commands through a velocity safety filter before publishing to the robot.

For a one-shot low-level check:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.05}, angular: {z: 0.0}}"
```

Then stop it:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

Learning point: `/cmd_vel` is the basic velocity command interface. Navigation stacks eventually output this same kind of command after planning.

## 4. RPLIDAR A1

Install or build the SLAMTEC ROS 2 driver if it is not already present. The output we need is:

```bash
ros2 topic echo /scan --once
```

Expected:

- Message type: `sensor_msgs/msg/LaserScan`
- Range values change when an object moves in front of the LiDAR.

Learning point: a 2D LiDAR gives range measurements around the robot. SLAM and obstacle avoidance use those ranges to estimate free and occupied space.

## 5. Camera

Start the default Raspberry Pi libcamera stream:

```bash
ros2 launch autonomous_tour_guide camera_stream.launch.py
```

The default libcamera pixel format is `RGB888`, which avoids `nv21` images that `rqt_image_view` cannot display.

For a USB camera or a camera exposed as a working V4L2 device:

```bash
ros2 launch autonomous_tour_guide camera_stream.launch.py camera_backend:=v4l2 video_device:=/dev/video0
```

The first useful check is simply that frames arrive:

```bash
ros2 topic list | rg image
```

Expected:

- A camera image topic, usually `sensor_msgs/msg/Image`.

Learning point: camera data is high-bandwidth. It is useful for platform video, AI perception, and incident review, but expensive to stream continuously.

## 6. TF Frames

Check transforms:

```bash
ros2 run tf2_tools view_frames
```

Expected frame chain:

```text
map -> odom -> base_link -> laser
```

Early bring-up may only have:

```text
odom -> base_link
```

Learning point: TF is how ROS represents where every sensor and robot part is. Navigation fails when transforms are missing or wrong.

## 7. Visualization

Run RViz:

```bash
rviz2
```

Add displays:

- TF
- LaserScan on `/scan`
- Odometry
- Map
- RobotModel if available

Learning point: RViz is your first debugging dashboard. Before cloud platforms, prove the robot state locally.
