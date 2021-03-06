FROM python:3.9.2-buster

WORKDIR /opt/project

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .

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
    && pip install poetry==1.1.4

# TODO(dmu) LOW: Optimize images size by not installing development dependencies
#                (have another image for running unittests)
# We need development dependencies installed to be able to run dockerized unittests
RUN poetry export --without-hashes --dev -f requirements.txt -o requirements.txt \
    && pip install --no-cache-dir -r requirements.txt

# Copy everything here for docker build optimization purposes
# We do not use just `COPY . .` to avoid accidental inclusion sensitive information from
# developers' machines into an image
COPY scripts/run.sh .
RUN chmod a+x run.sh

COPY Makefile .
COPY thenewboston_node thenewboston_node
