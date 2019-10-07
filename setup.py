from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="uitestcore",
    version="5.1.1",
    description="Package providing common functionality for UI automation test packs",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    homepage="https://github.com/nhsuk/ui-test-core/",
    packages=["uitestcore", "uitestcore.utilities"],
    install_requires=[
        "certifi==2019.6.16",
        "chardet==3.0.4",
        "idna==2.8",
        "pyhamcrest==1.9.0",
        "python-dateutil==2.8.0",
        "requests==2.21.0",
        "selenium==3.141.0",
        "six==1.12.0",
        "urllib3==1.24.3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ]
)
