from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "start_keyboard",
                default_value="true",
                description="Start teleop_twist_keyboard as the manual command source.",
            ),
            DeclareLaunchArgument(
                "teleop_cmd_vel_topic",
                default_value="/tour_guide/manual_cmd_vel",
                description="Intermediate manual command topic from teleop input.",
            ),
            DeclareLaunchArgument(
                "cmd_vel_topic",
                default_value="/cmd_vel",
                description="Robot velocity command topic.",
            ),
            DeclareLaunchArgument(
                "max_linear_mps",
                default_value="0.20",
                description="Maximum linear x speed allowed through the safety filter.",
            ),
            DeclareLaunchArgument(
                "max_angular_radps",
                default_value="0.75",
                description="Maximum angular z speed allowed through the safety filter.",
            ),
            DeclareLaunchArgument(
                "command_timeout_sec",
                default_value="0.75",
                description="Stop the robot when no manual command has arrived for this long.",
            ),
            DeclareLaunchArgument(
                "publish_period_sec",
                default_value="0.10",
                description="Safety filter publish period.",
            ),
            Node(
                package="autonomous_tour_guide",
                executable="manual_velocity_filter",
                name="manual_velocity_filter",
                output="screen",
                parameters=[
                    {
                        "input_topic": LaunchConfiguration("teleop_cmd_vel_topic"),
                        "output_topic": LaunchConfiguration("cmd_vel_topic"),
                        "max_linear_mps": LaunchConfiguration("max_linear_mps"),
                        "max_angular_radps": LaunchConfiguration("max_angular_radps"),
                        "command_timeout_sec": LaunchConfiguration("command_timeout_sec"),
                        "publish_period_sec": LaunchConfiguration("publish_period_sec"),
                    }
                ],
            ),
            Node(
                package="teleop_twist_keyboard",
                executable="teleop_twist_keyboard",
                name="keyboard_teleop",
                output="screen",
                emulate_tty=True,
                condition=IfCondition(LaunchConfiguration("start_keyboard")),
                remappings=[
                    ("cmd_vel", LaunchConfiguration("teleop_cmd_vel_topic")),
                ],
            ),
        ]
    )
