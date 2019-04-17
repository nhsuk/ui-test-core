from setuptools import setup

setup(
   name="ui_automation_core",
   version="0.1.1",
   description="Module providing common functionality for UI automation test packs",
   author="Phil Turner",
   author_email="philip.turner9@nhs.net",
   packages=["ui_automation_core"],
   install_requires=["selenium==3.11.0"]
)
