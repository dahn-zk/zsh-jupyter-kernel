#!/usr/bin/env zsh
version=`cat version`
git tag -a $version -m $version
git push --follow-tags