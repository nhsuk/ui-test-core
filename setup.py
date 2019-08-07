from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="uitestcore",
    version="2.4.1",
    description="Package providing common functionality for UI automation test packs",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=["uitestcore", "uitestcore.utilities"],
    install_requires=[
        "behave==1.2.6",
        "PyHamcrest==1.9.0",
        "selenium==3.141.0",
        "requests==2.21.0",
        "urllib3==1.24.3",
        "python-dateutil==2.8.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ]
)
