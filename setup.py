from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="uitestcore",
    version="7.0.0.2",
    description="Package providing common functionality for UI automation test packs",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    homepage="https://github.com/nhsuk/ui-test-core/",
    packages=["uitestcore", "uitestcore.utilities"],
    install_requires=[
        "certifi==2021.5.30",
        "chardet==4.0.0",
        "idna==3.2",
        "pyhamcrest==2.0.2",
        "python-dateutil==2.8.1",
        "requests==2.25.1",
        "selenium==3.141.0",
        "six==1.16.0",
        "urllib3==1.26.5"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ]
)
