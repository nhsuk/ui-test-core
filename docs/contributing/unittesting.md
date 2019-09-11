# Unit Tests

The unit tests for this package can be found in the tests folder and are written using PyTest.

## Required coverage rate
We require a minimum coverage rate of 95%

## How to run
**Rquires:** [pytest](https://pypi.org/project/pytest/)

In the root of the project, run the following command:
``` bash
pytest --cov=uitestcore --cov-fail-under=95 --cov-report term-missing --junitxml='reports/junit/unit-tests.xml'
```