# An attempt to make a minimal image
# Does not work

FROM alpine:3.11.2

RUN apk update
RUN apk add zsh

RUN apk add python3 libzmq
RUN apk add build-base musl-dev python3-dev zeromq-dev
RUN python3 -m pip install pyzmq
RUN apk del build-base musl-dev python3-dev zeromq-dev

RUN python3 -m pip install notebook zsh_jupyter_kernel
RUN python3 -m zsh_jupyter_kernel.install --sys-prefix

RUN addgroup -S oak
RUN adduser -S dan -G oak -h /test
USER dan

EXPOSE 8889 80 443

CMD [ "jupyter", "notebook", "--ip=0.0.0.0", "--port=8889", "--allow-root" ]
