from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_arg(context, name: str) -> str:
    return LaunchConfiguration(name).perform(context)


def int_launch_arg(context, name: str) -> int:
    return int(launch_arg(context, name))


def camera_nodes(context, *args, **kwargs):
    backend = launch_arg(context, "camera_backend").strip().lower()
    image_width = int_launch_arg(context, "image_width")
    image_height = int_launch_arg(context, "image_height")
    frame_rate = int_launch_arg(context, "frame_rate")
    camera_frame_id = launch_arg(context, "camera_frame_id")
    image_topic = launch_arg(context, "image_topic")
    camera_info_topic = launch_arg(context, "camera_info_topic")

    if backend == "v4l2":
        parameters = {
            "video_device": launch_arg(context, "video_device"),
            "pixel_format": launch_arg(context, "v4l2_pixel_format"),
            "output_encoding": launch_arg(context, "output_encoding"),
            "image_size": [image_width, image_height],
            "camera_frame_id": camera_frame_id,
        }
        if frame_rate > 0:
            parameters["time_per_frame"] = [1, frame_rate]

        return [
            Node(
                package="v4l2_camera",
                executable="v4l2_camera_node",
                name="camera",
                output="screen",
                parameters=[parameters],
                remappings=[
                    ("image_raw", image_topic),
                    ("camera_info", camera_info_topic),
                ],
            )
        ]

    if backend == "libcamera":
        libcamera_selector = launch_arg(context, "libcamera_selector")
        parameters = {
            "camera": int(libcamera_selector) if libcamera_selector.isdecimal() else libcamera_selector,
            "role": "viewfinder",
            "width": image_width,
            "height": image_height,
            "frame_id": camera_frame_id,
        }
        libcamera_format = launch_arg(context, "libcamera_format").strip()
        if libcamera_format:
            parameters["format"] = libcamera_format
        if frame_rate > 0:
            frame_duration_us = int(1_000_000 / frame_rate)
            parameters["FrameDurationLimits"] = [frame_duration_us, frame_duration_us]

        return [
            Node(
                package="camera_ros",
                executable="camera_node",
                name="camera",
                output="screen",
                parameters=[parameters],
                remappings=[
                    ("image_raw", image_topic),
                    ("camera_info", camera_info_topic),
                ],
            )
        ]

    raise RuntimeError("camera_backend must be 'v4l2' or 'libcamera'")


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "camera_backend",
                default_value="libcamera",
                description="Camera driver backend: 'v4l2' for v4l2_camera or 'libcamera' for camera_ros.",
            ),
            DeclareLaunchArgument(
                "video_device",
                default_value="/dev/video0",
                description="V4L2 camera device path.",
            ),
            DeclareLaunchArgument(
                "libcamera_selector",
                default_value="0",
                description="camera_ros camera selector, either a camera index or libcamera camera name.",
            ),
            DeclareLaunchArgument(
                "v4l2_pixel_format",
                default_value="YUYV",
                description="V4L2 FOURCC pixel format requested from the camera.",
            ),
            DeclareLaunchArgument(
                "libcamera_format",
                default_value="",
                description="Optional camera_ros pixel format. Leave empty to let libcamera choose.",
            ),
            DeclareLaunchArgument(
                "output_encoding",
                default_value="rgb8",
                description="ROS image encoding produced by v4l2_camera.",
            ),
            DeclareLaunchArgument(
                "image_width",
                default_value="640",
                description="Requested camera image width.",
            ),
            DeclareLaunchArgument(
                "image_height",
                default_value="480",
                description="Requested camera image height.",
            ),
            DeclareLaunchArgument(
                "frame_rate",
                default_value="15",
                description="Requested frame rate. Use 0 to leave the driver default.",
            ),
            DeclareLaunchArgument(
                "camera_frame_id",
                default_value="camera_link_optical",
                description="Frame id stamped on camera messages.",
            ),
            DeclareLaunchArgument(
                "image_topic",
                default_value="/camera/image_raw",
                description="Published image topic.",
            ),
            DeclareLaunchArgument(
                "camera_info_topic",
                default_value="/camera/camera_info",
                description="Published camera info topic.",
            ),
            OpaqueFunction(function=camera_nodes),
        ]
    )
