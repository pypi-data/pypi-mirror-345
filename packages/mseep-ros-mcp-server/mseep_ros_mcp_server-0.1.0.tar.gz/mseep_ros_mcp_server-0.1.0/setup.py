
from setuptools import setup, find_packages

setup(
    name="mseep-ros-mcp-server",
    version="0.1.0",
    description="Add your description here",
    author="mseep",
    author_email="support@skydeck.ai",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['mcp[cli]>=1.6.0', 'opencv-python>=4.11.0.86', 'websocket>=0.2.1', 'websocket-client>=1.8.0'],
    keywords=["mseep"] + [],
)
