# Linting

Pylint is being used to ensure code quality. We're following the [PEP8](https://www.python.org/dev/peps/pep-0008) standard.

## Required score
We require a minimum score of 9.5

## How to run

**Requires:** [pylint-fail-under](https://pypi.org/project/pylint-fail-under/)

In the root of the project, run the following command:
``` bash
pylint-fail-under --fail_under 9.5 uitestcore
```