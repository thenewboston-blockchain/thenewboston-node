FROM python:3.9.2-buster AS node

ARG BLOCKCHAIN_STATE_NODE_ADDRESS=http://3.143.205.184:8555/

WORKDIR /opt/project

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
ENV IN_DOCKER true

EXPOSE 8555

COPY LICENSE .

COPY pyproject.toml .
COPY poetry.lock .

# TODO(dmu) LOW: Optimize images size by deleting no longer needed files after installation
RUN set -xe \
    && apt-get update \
    && apt-get install build-essential \
    && pip install pip==21.0.1 \
    && pip install virtualenvwrapper \
    && pip install poetry==1.1.4 \
    && poetry run pip install pip==21.0.1

# TODO(dmu) LOW: Optimize images size by not installing development dependencies
#                (have another image for running unittests)
# We need development dependencies installed to be able to run dockerized unittests
RUN poetry export --without-hashes --dev -f requirements.txt -o requirements.txt \
    && poetry run pip install --no-cache-dir -r requirements.txt

# Copy everything here for docker build optimization purposes
# We do not use just `COPY . .` to avoid accidental inclusion sensitive information from
# developers' machines into an image
COPY scripts/run.sh .
RUN chmod a+x run.sh

RUN mkdir -p /var/lib/blockchain_volume/blockchain
ENV THENEWBOSTON_NODE_BLOCKCHAIN '{"kwargs":{"base_directory":"/var/lib/blockchain_volume/blockchain"}}'

COPY Makefile .
COPY conftest.py .
COPY README.rst .

COPY thenewboston_node thenewboston_node
RUN poetry install
RUN make docs-html && make docs-rst

ENV ARF_URL https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/latest.json
ENV ARF_PATH /opt/project/alpha-arf-latest.json
RUN curl ${ARF_URL} -o ${ARF_PATH}

ENV BLOCKCHAIN_STATE_PATH /opt/project/blockchain-state.msgpack

# TODO(dmu) LOW: Should we move the following line to the top of the file?
ARG RESET_DOCKER_CACHE=default
RUN echo ${RESET_DOCKER_CACHE}  # Reset cache here
RUN THENEWBOSTON_NODE_SECRET_KEY=default poetry run python -m thenewboston_node.manage download_latest_blockchain_state ${BLOCKCHAIN_STATE_NODE_ADDRESS} --target "${BLOCKCHAIN_STATE_PATH}{compressor}" || echo "Unable to get beta blockchain state from ${BLOCKCHAIN_STATE_NODE_ADDRESS}"

FROM nginx:1.19.10-alpine AS reverse-proxy

RUN rm /etc/nginx/conf.d/default.conf
COPY ./thenewboston_node/project/settings/templates/nginx.conf /etc/nginx/conf.d/node.conf

COPY --from=node /opt/project/docs/thenewboston-blockchain-format.html /var/www/blockchain-docs/index.html
COPY --from=node /opt/project/docs/thenewboston-blockchain-format.rst /var/www/blockchain-docs/index.rst
