from glob import glob
from setuptools import setup

package_name = "autonomous_tour_guide"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
        (f"share/{package_name}/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Ariel Corte",
    maintainer_email="ariel@example.com",
    description="Create 3 autonomous tour guide demo orchestration and telemetry.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "manual_velocity_filter = autonomous_tour_guide.manual_velocity_filter:main",
            "mission_status_publisher = autonomous_tour_guide.mission_status_publisher:main",
            "waypoint_runner = autonomous_tour_guide.waypoint_runner:main",
        ],
    },
)
