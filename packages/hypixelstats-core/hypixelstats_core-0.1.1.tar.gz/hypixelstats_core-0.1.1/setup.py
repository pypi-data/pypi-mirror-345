from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hypixelstats-core",
    version="0.1.1",
    author="seolhwa",
    description="A lightweight Hypixel statistics module.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        "hypixel_stats",
        "hypixel_stats.games",
        "hypixel_stats.utils"
    ],
    include_package_data=True,
    license="Custom",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
)
