from setuptools import setup, find_packages

setup(
	name="flagsense",
	version="0.1.3",
    description="A Python package for flag detection and classification in images, leveraging deep learning models for efficient and accurate results.",
    author="Timothy Loftus",
    author_email="tiloftus.4@gmail.com",
    url="https://github.com/tiloftus/flagsense",
	packages=find_packages(include=["flagsense", "flagsense.*"]),
	install_requires=[
		"ultralytics",
		"opencv-python",
        "requests"
	],
)
