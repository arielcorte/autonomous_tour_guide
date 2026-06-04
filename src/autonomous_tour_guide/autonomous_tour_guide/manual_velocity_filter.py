from __future__ import annotations

from dataclasses import dataclass

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.time import Time


@dataclass(frozen=True)
class VelocityLimits:
    max_linear_mps: float
    max_angular_radps: float


def clamp(value: float, limit: float) -> float:
    absolute_limit = abs(limit)
    return max(-absolute_limit, min(absolute_limit, value))


def zero_twist() -> Twist:
    return Twist()


class ManualVelocityFilter(Node):
    """Safety wrapper for manual velocity commands before they reach the robot."""

    def __init__(self) -> None:
        super().__init__("manual_velocity_filter")

        self.declare_parameter("input_topic", "/tour_guide/manual_cmd_vel")
        self.declare_parameter("output_topic", "/cmd_vel")
        self.declare_parameter("max_linear_mps", 0.20)
        self.declare_parameter("max_angular_radps", 0.75)
        self.declare_parameter("command_timeout_sec", 0.75)
        self.declare_parameter("publish_period_sec", 0.10)

        input_topic = str(self.get_parameter("input_topic").value)
        output_topic = str(self.get_parameter("output_topic").value)
        self.limits = VelocityLimits(
            max_linear_mps=float(self.get_parameter("max_linear_mps").value),
            max_angular_radps=float(self.get_parameter("max_angular_radps").value),
        )
        self.command_timeout_sec = max(0.05, float(self.get_parameter("command_timeout_sec").value))
        publish_period_sec = max(0.02, float(self.get_parameter("publish_period_sec").value))

        self.publisher = self.create_publisher(Twist, output_topic, 10)
        self.subscription = self.create_subscription(Twist, input_topic, self.store_command, 10)
        self.timer = self.create_timer(publish_period_sec, self.publish_command)

        self.current_command = zero_twist()
        self.last_command_time: Time | None = None
        self.command_active = False

        self.get_logger().info(
            "Manual velocity filter listening on "
            f"{input_topic} and publishing limited commands to {output_topic} "
            f"(linear <= {self.limits.max_linear_mps:.2f} m/s, "
            f"angular <= {self.limits.max_angular_radps:.2f} rad/s)"
        )

    def store_command(self, message: Twist) -> None:
        self.current_command = self.limit_command(message)
        self.last_command_time = self.get_clock().now()
        self.command_active = True

    def limit_command(self, message: Twist) -> Twist:
        limited = zero_twist()
        limited.linear.x = clamp(float(message.linear.x), self.limits.max_linear_mps)
        limited.angular.z = clamp(float(message.angular.z), self.limits.max_angular_radps)
        return limited

    def publish_command(self) -> None:
        if self.command_timed_out():
            if self.command_active:
                self.get_logger().warn("Manual command timed out; publishing stop command")
            self.current_command = zero_twist()
            self.command_active = False

        self.publisher.publish(self.current_command)

    def command_timed_out(self) -> bool:
        if self.last_command_time is None:
            return True

        age = self.get_clock().now() - self.last_command_time
        return age.nanoseconds > int(self.command_timeout_sec * 1_000_000_000)

    def stop_robot(self) -> None:
        self.publisher.publish(zero_twist())


def main() -> None:
    rclpy.init()
    node = ManualVelocityFilter()
    try:
        rclpy.spin(node)
    finally:
        node.stop_robot()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
