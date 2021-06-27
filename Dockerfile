FROM python:3.9.2-buster

WORKDIR /opt/project

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
ENV IN_DOCKER true

EXPOSE 8000

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

RUN mkdir -p /etc/nginx/conf.d
COPY thenewboston_node/project/settings/templates/nginx.conf /etc/nginx/conf.d/node.conf

RUN mkdir -p /var/lib/blockchain
ENV THENEWBOSTON_NODE_BLOCKCHAIN '{"kwargs":{"base_directory":"/var/lib/blockchain"}}'

COPY Makefile .
COPY conftest.py .
COPY README.rst .

COPY thenewboston_node thenewboston_node
RUN poetry install
ENV ARF_URL https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/latest.json
ENV ARF_PATH /opt/project/alpha-arf-latest.json
RUN curl ${ARF_URL} -o ${ARF_PATH}
