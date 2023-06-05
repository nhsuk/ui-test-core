from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="uitestcore",
    version="10.3.20230505.2",
    description="Package providing common functionality for UI automation test packs",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    homepage="https://github.com/nhsuk/ui-test-core/",
    packages=["uitestcore", "uitestcore.utilities"],
    install_requires=[
        "certifi==2023.5.7",
        "chardet==5.1.0",
        "idna==3.4",
        "pyhamcrest==2.0.4",
        "python-dateutil==2.8.2",
        "requests==2.31.0",
        "selenium==4.9.1",
        "six==1.16.0",
        "urllib3==1.26.12",
        "axe-selenium-python-nhsuk"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ]
)
