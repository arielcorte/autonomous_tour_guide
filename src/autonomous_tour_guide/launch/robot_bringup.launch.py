from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = Path(get_package_share_directory("autonomous_tour_guide"))
    launch_dir = package_share / "launch"

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "mission_id",
                default_value="room_tour_demo",
                description="Mission id used by demo telemetry.",
            ),
            DeclareLaunchArgument(
                "status_publish_period_sec",
                default_value="1.0",
                description="Mission status publisher period.",
            ),
            DeclareLaunchArgument(
                "start_status",
                default_value="true",
                description="Start the demo mission status publisher.",
            ),
            DeclareLaunchArgument(
                "start_camera",
                default_value="true",
                description="Start the camera stream launch.",
            ),
            DeclareLaunchArgument(
                "start_manual_control",
                default_value="false",
                description="Start keyboard manual control and velocity safety filter.",
            ),
            DeclareLaunchArgument(
                "camera_backend",
                default_value="v4l2",
                description="Camera driver backend: 'v4l2' or 'libcamera'.",
            ),
            DeclareLaunchArgument("video_device", default_value="/dev/video0"),
            DeclareLaunchArgument("libcamera_selector", default_value="0"),
            DeclareLaunchArgument("v4l2_pixel_format", default_value="YUYV"),
            DeclareLaunchArgument("libcamera_format", default_value=""),
            DeclareLaunchArgument("output_encoding", default_value="rgb8"),
            DeclareLaunchArgument("image_width", default_value="640"),
            DeclareLaunchArgument("image_height", default_value="480"),
            DeclareLaunchArgument("frame_rate", default_value="15"),
            DeclareLaunchArgument("camera_frame_id", default_value="camera_link_optical"),
            DeclareLaunchArgument("image_topic", default_value="/camera/image_raw"),
            DeclareLaunchArgument("camera_info_topic", default_value="/camera/camera_info"),
            DeclareLaunchArgument("start_keyboard", default_value="true"),
            DeclareLaunchArgument("teleop_cmd_vel_topic", default_value="/tour_guide/manual_cmd_vel"),
            DeclareLaunchArgument("cmd_vel_topic", default_value="/cmd_vel"),
            DeclareLaunchArgument("max_linear_mps", default_value="0.20"),
            DeclareLaunchArgument("max_angular_radps", default_value="0.75"),
            DeclareLaunchArgument("command_timeout_sec", default_value="0.75"),
            DeclareLaunchArgument("publish_period_sec", default_value="0.10"),
            Node(
                package="autonomous_tour_guide",
                executable="mission_status_publisher",
                name="mission_status_publisher",
                output="screen",
                condition=IfCondition(LaunchConfiguration("start_status")),
                parameters=[
                    {
                        "mission_id": LaunchConfiguration("mission_id"),
                        "publish_period_sec": LaunchConfiguration("status_publish_period_sec"),
                    }
                ],
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(launch_dir / "camera_stream.launch.py")),
                condition=IfCondition(LaunchConfiguration("start_camera")),
                launch_arguments={
                    "camera_backend": LaunchConfiguration("camera_backend"),
                    "video_device": LaunchConfiguration("video_device"),
                    "libcamera_selector": LaunchConfiguration("libcamera_selector"),
                    "v4l2_pixel_format": LaunchConfiguration("v4l2_pixel_format"),
                    "libcamera_format": LaunchConfiguration("libcamera_format"),
                    "output_encoding": LaunchConfiguration("output_encoding"),
                    "image_width": LaunchConfiguration("image_width"),
                    "image_height": LaunchConfiguration("image_height"),
                    "frame_rate": LaunchConfiguration("frame_rate"),
                    "camera_frame_id": LaunchConfiguration("camera_frame_id"),
                    "image_topic": LaunchConfiguration("image_topic"),
                    "camera_info_topic": LaunchConfiguration("camera_info_topic"),
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(launch_dir / "manual_control.launch.py")),
                condition=IfCondition(LaunchConfiguration("start_manual_control")),
                launch_arguments={
                    "start_keyboard": LaunchConfiguration("start_keyboard"),
                    "teleop_cmd_vel_topic": LaunchConfiguration("teleop_cmd_vel_topic"),
                    "cmd_vel_topic": LaunchConfiguration("cmd_vel_topic"),
                    "max_linear_mps": LaunchConfiguration("max_linear_mps"),
                    "max_angular_radps": LaunchConfiguration("max_angular_radps"),
                    "command_timeout_sec": LaunchConfiguration("command_timeout_sec"),
                    "publish_period_sec": LaunchConfiguration("publish_period_sec"),
                }.items(),
            ),
        ]
    )
