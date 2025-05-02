from setuptools import setup

setup(
    name="rtspcheck",
    version="1.0.1",
    description="RtspCheck is a Camera Port and Stream Checker used to find open cameras",
    author="Babar Ali Jamali",
    author_email="babar995@gmail.com",
    packages=["rtspcheck"],  # This should match the folder name inside
    install_requires=[
        "opencv-python",
        "numpy",
        "ipaddress",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'rtspcheck = rtspcheck.rtspcheck:main',  # Adjusted to match the package structure
        ],
    },
)
