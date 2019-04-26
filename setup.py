from setuptools import setup

setup(
   name="ui_automation_core",
   version="0.1.5",
   description="Module providing common functionality for UI automation test packs",
   author="Phil Turner",
   author_email="philip.turner9@nhs.net",
   packages=["ui_automation_core", "ui_automation_core.utilities"],
   install_requires=["selenium==3.11.0", "PyHamcrest==1.9.0", "requests==2.21.0"]
)
