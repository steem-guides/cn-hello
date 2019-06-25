#!/bin/sh

set -e

[ "${TRAVIS_BRANCH}" != "master" ] && exit 0

pipenv run invoke cn-hello.welcome -d 3
pipenv run invoke cn-hello.daily-stats -d 3
sleep 300 # sleep 5 minutes to avoid the post too frequently issue
pipenv run invoke cn-hello.weekly-stats -d 3
