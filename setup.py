from setuptools import setup

setup(
   name="ui_automation_core",
   version="1.7.0",
   description="Module providing common functionality for automation test packs",
   packages=["ui_automation_core", "ui_automation_core.utilities"],
   install_requires=["selenium==3.141.0",
                     "PyHamcrest==1.9.0",
                     "urllib3==1.24.3",
                     "requests==2.21.0",
                     "behave==1.2.6",
                     "python-dateutil==2.8.0",
                     "pytest==4.5"
                     ]
)
