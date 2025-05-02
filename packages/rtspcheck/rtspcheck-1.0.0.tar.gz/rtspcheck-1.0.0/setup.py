from setuptools import setup

setup(
    name="rtspcheck",  # Project name
    version="1.0.0",  # Version
    author="Babar Ali Jamali",
    author_email="babar995@gmail.com",
    description="RtspCheck is a Camera Port and Stream Checker used to find open cameras",
    long_description="RtspCheck is a Camera Port and Stream Checker used to find open cameras",
    long_description_content_type="text/plain",
    url="https://github.com/babaralijamali/RtspCheck",  # Update with your GitHub URL if applicable
    py_modules=["rtspcheck"],  # The main script file
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
    python_requires=">=3.6",  # Minimum Python version required
)
