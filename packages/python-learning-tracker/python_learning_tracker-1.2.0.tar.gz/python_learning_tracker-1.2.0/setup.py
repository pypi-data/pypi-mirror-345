from setuptools import find_packages, setup

setup(
    name="python_learning_tracker",
    version="1.0.0",
    description="Python Learning Tracker - аналіз прогресу у вивченні Python",
    author="",
    author_email="",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pytest>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "learning-tracker=python_learning_tracker.cli:main",
        ],
    },
)
