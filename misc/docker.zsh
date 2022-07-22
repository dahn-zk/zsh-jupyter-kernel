#!/usr/bin/env zsh

v=$(<./src/zsh_jupyter_kernel/version)
t=zsh-jupyter-kernel:$v

case $1 in
  build)
    docker build --tag $t .
    ;;
  run)
    docker run --rm --interactive --tty \
      --publish=8889:8888 \
      --volume=$PWD/test:/home/jovyan \
      --name=zsh-jupyter-kernel \
      $t
    ;;
esac
