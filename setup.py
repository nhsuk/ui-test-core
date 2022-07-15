from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="uitestcore",
    version="8.0.20220715",
    description="Package providing common functionality for UI automation test packs",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    homepage="https://github.com/nhsuk/ui-test-core/",
    packages=["uitestcore", "uitestcore.utilities"],
    install_requires=[
        "certifi==2022.6.15",
        "chardet==5.0.0",
        "idna==3.3",
        "pyhamcrest==2.0.2",
        "python-dateutil==2.8.2",
        "requests==2.28.1",
        "selenium==4.3.0",
        "six==1.16.0",
        "urllib3==1.26.9"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ]
)
