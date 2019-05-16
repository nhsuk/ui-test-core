#!/bin/bash

### When running automated test jobs in Azure, we've seen that the build agent can't always "see" the target URL.
### When this happens, each individual test will try to run and timeout. The issue with that is the timeout is 30 seconds. 
### If the test pack contains 100 tests that means the build will be running for 50 minutes. 
### That causes the other jobs to wait and delays other peoples work.
### This has the potential to block deployments.
### Chris Midgley suggested that if the agent can't see the URL then the tests should be skipped and the build failed fast. 


if [[ ! -z "$1" ]]
  then
    echo "### You provided the arguments:" "$@"
    echo "### Setting first argument as target URL with https:// added"
    TARGET_URL="https://"$1
    echo $TARGET_URL
fi

echo '### Checking my own IP address'
IP=$(curl -s ifconfig.me)
echo $IP

echo '### Checking URL access'
PYTHON_SCRIPT='import urllib.request as r; x = r.urlopen(r.Request("'${TARGET_URL}'", headers={"User-Agent": "Mozilla/5.0"})); print(f"Status Code was {x.code}");'
docker run --rm python:3.7-alpine3.9 python3 -c "$PYTHON_SCRIPT"
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then 
    echo "### Couldn't resolve target url: ${TARGET_URL}"
    echo "### Failing the build to prevent tests attempting to run"
    exit $EXIT_CODE; 
fi