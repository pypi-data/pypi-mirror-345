from setuptools import setup, find_packages

setup(
    name="RtspScan",
    version="1.0.0",  # Version updated
    description="RtspScan is a Port Scanner and Streamer used to scan and open any camera connected to the internet.",
    author="Babar Ali Jamali",
    author_email="babar995@gmail.com",
    url="https://github.com/babaralijamali/RtspScan",
    packages=find_packages(),
    install_requires=[
        'opencv-python',
    ],
    entry_points={
        'console_scripts': [
            'rtspscan = rtspscan:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
