# minimal-notebook version from Feb 8, 2021
FROM jupyter/minimal-notebook:016833b15ceb 

USER root

RUN apt update
RUN apt upgrade --quiet --assume-yes --no-install-recommends
RUN apt install --quiet --assume-yes --no-install-recommends zsh
# uncomment to test oh-my-zsh
# RUN sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

RUN python3 -m pip install zsh_jupyter_kernel
RUN python3 -m zsh_jupyter_kernel.install --sys-prefix

RUN apt install --quiet --assume-yes --no-install-recommends figlet

ENV JUPYTER_RUNTIME_DIR "/tmp"
CMD [ "jupyter", "notebook", "--allow-root" ]
