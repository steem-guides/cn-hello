#!/bin/sh

set -e

[ "${TRAVIS_BRANCH}" != "master" ] && exit 0

pipenv run invoke cn-hello.welcome -d 3
pipenv run invoke cn-hello.summarize -d 3
