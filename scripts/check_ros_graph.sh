#!/usr/bin/env bash
set -euo pipefail

ROS_SETUP=${ROS_SETUP:-/opt/ros/humble/setup.bash}

if [ -f "$ROS_SETUP" ]; then
  # shellcheck source=/opt/ros/humble/setup.bash
  set +u
  source "$ROS_SETUP"
  set -u
else
  echo "ROS setup file not found: $ROS_SETUP" >&2
fi

if [ -f install/setup.bash ]; then
  set +u
  source install/setup.bash
  set -u
fi

echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
echo "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-unset}"
echo "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-unset}"
echo "ROS_LOCALHOST_ONLY=${ROS_LOCALHOST_ONLY:-unset}"
echo
echo "Nodes:"
ros2 node list || true
echo
echo "Topics:"
topics=$(ros2 topic list -t 2>&1 || true)
printf "%s\n" "$topics"

if ! printf "%s\n" "$topics" | grep -Eq 'irobot_create_msgs|/pada_1/|/battery_state|/cmd_vel'; then
  cat <<'EOF'

No obvious Create 3 topics found.
If the Raspberry Pi can see them but this shell cannot, check:
- this shell has sourced /opt/ros/humble/setup.bash,
- ROS_DOMAIN_ID matches the Pi and Create 3,
- ROS_LOCALHOST_ONLY is unset or 0,
- the distrobox is using host networking,
- the ROS daemon has been restarted after environment changes.
EOF
fi
