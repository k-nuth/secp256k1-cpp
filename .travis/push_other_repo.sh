#!/bin/bash

echo "Travis branch: ${TRAVIS_BRANCH}"
echo "Travis tag: ${TRAVIS_TAG}"

if [[ ${TRAVIS_BRANCH} == ${TRAVIS_TAG} ]]; then
    export KNUTH_PUSH_BRANCH=master
else
    export KNUTH_PUSH_BRANCH=${TRAVIS_BRANCH}
fi
echo "Knuth branch: ${KNUTH_PUSH_BRANCH}"


# TODO(fernando): put in another place
export KNUTH_PUSH_ACCOUNT=knuth
export KNUTH_PUSH_PROJECT=knuth-core

# body="{
#     \"accountName\": \"knuth\",
#     \"projectSlug\": \"knuth-core\",
#     \"branch\": \"${KNUTH_PUSH_BRANCH}\",
#     \"environmentVariables\": {
#        \"SKIP_NUGET\": \"true\"
#     }
# }"


body="{
    \"accountName\": \"${KNUTH_PUSH_ACCOUNT}\",
    \"projectSlug\": \"${KNUTH_PUSH_PROJECT}\",
    \"branch\": \"${KNUTH_PUSH_BRANCH}\"
}"

curl -s -d "$body" -X POST \
    -H "Authorization: Bearer ${APPVEYOR_TOKEN}" \
    -H "Content-Type: application/json" \
    https://ci.appveyor.com/api/builds

body="{
    \"request\": {
    \"branch\":\"${KNUTH_PUSH_BRANCH}\",
    \"message\": \"Force by secp256k1 build: ${TRAVIS_BUILD_NUMBER}\"
}}"

curl -s -X POST \
   -H "Content-Type: application/json" \
   -H "Accept: application/json" \
   -H "Travis-API-Version: 3" \
   -H "Authorization: token ${TRAVIS_TOKEN}" \
   -d "$body" \
   https://api.travis-ci.org/repo/${KNUTH_PUSH_ACCOUNT}%2F${KNUTH_PUSH_PROJECT}/requests





