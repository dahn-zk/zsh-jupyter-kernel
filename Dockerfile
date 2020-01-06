FROM jupyter/base-notebook:python-3.7.3

USER root

RUN apt-get update
RUN apt-get install --quiet --assume-yes --no-install-recommends zsh git
RUN sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

RUN python3 -m pip install notebook zsh_jupyter_kernel
RUN python3 -m zsh_jupyter_kernel.install --sys-prefix

CMD [ "jupyter", "notebook", "--allow-root" ]
