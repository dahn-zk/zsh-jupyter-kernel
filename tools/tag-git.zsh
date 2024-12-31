#!/usr/bin/env zsh
version=`cat zsh_jupyter_kernel/version.txt`
git tag -a $version -m $version
git push --follow-tags
