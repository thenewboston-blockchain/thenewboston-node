Local development environment setup
===================================

This section describes how to setup development environment for Debian-based distributions
(tested on Linux Mint 18.3 specifically)

Initial setup
+++++++++++++
Once initial setup is done only corresponding `Update`_ section should be performed
to get the latest version for development.

#. Install prerequisites::

    apt update
    apt install git

#. [if you have not configured it globally] Configure git::

    git config user.name 'Firstname Lastname'
    git config user.email 'youremail@youremail_domain.com'

#. Install prerequisites (
   as prescribed at https://github.com/pyenv/pyenv/wiki/Common-build-problems )::

    # TODO(dmu) MEDIUM: Remove those that are not really needed
    apt update && \
    apt install make build-essential libssl-dev zlib1g-dev libbz2-dev \
                libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
                libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl

#. Install Docker according to https://docs.docker.com/engine/install/
   (known working: Docker version 20.10.1, build 831ebea)
#. Add your user to docker group::

    sudo usermod -aG docker $USER
    exit

#. Install Docker Compose according to https://docs.docker.com/compose/install/
   (known working: docker-compose version 1.27.4, build 40524192)

#. Fork https://github.com/thenewboston-developers/thenewboston-node repository
#. Clone the fork::

    git clone git@github.com:thenewboston-developers/thenewboston-node.git

#. Add https://github.com/thenewboston-developers/thenewboston-node as upstream::

    cd thenewboston-node
    git remote add upstream git@github.com:thenewboston-developers/thenewboston-node.git
    git fetch upstream

#. Install and configure `pyenv` according to https://github.com/pyenv/pyenv#basic-github-checkout
#. Install lowest supported Python version::

    pyenv install 3.9.2
    pyenv local 3.9.2  # run from the root of this repo (`.python-version` file should appear)

#. Install Poetry::

    export PIP_REQUIRED_VERSION=21.0.1
    pip install pip==${PIP_REQUIRED_VERSION} && \
    pip install virtualenvwrapper && \
    pip install poetry==1.1.4 && \
    poetry config virtualenvs.path ${HOME}/.virtualenvs && \
    poetry run pip install pip==${PIP_REQUIRED_VERSION}

#. Setup local configuration for running code on host::

    mkdir local
    cp thenewboston_node/project/settings/templates/settings.py ./local/settings.py
    cp thenewboston_node/project/settings/templates/settings.unittests.py ./local/settings.unittests.py

    # Edit files if needed
    vim ./local/settings.py
    vim ./local/settings.unittests.py

#. Setup local configuration for running docker image::

    cp thenewboston_node/project/settings/templates/.env .
    vim .env  # edit file if needed

#. Install dependencies, run migrations, etc by doing `Update`_ section steps
#. Create superuser::

    make create-superuser

#. Generate sample blockchain::

    # Generate account numbers will be logged on INFO level
    mkdir -p local/blockchain
    generate-blockchain --path local/blockchain --do-not-validate 200

Update
++++++
#. (in a separate terminal) Run dependency services::

    make up-dependencies-only

#. Update::

    make update

Lint
++++

#. Lint::

    make lint

Run
+++

#. (in a separate terminal) Run only dependency services with Docker::

    make up-dependencies-only

#. (in a separate terminal) Run Node::

    make run-server

Hints
=====

#. If you would like to gitignore some directories/files specific to your local dev env setup
   use `.git/info/exclude` of the local repository instead of adding them to `.gitignore`
