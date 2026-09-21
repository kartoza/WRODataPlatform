FROM python:3.9-slim-bullseye

# bullseye is EOL: deb.debian.org no longer serves its packages, so switch to
# the pinned snapshot.debian.org mirror the base image already ships (commented
# out) as a fallback for exactly this situation. The pinned snapshot date is
# itself always going to be "in the past", so disable apt's Release
# expiry check too - that's expected/required when using snapshot.debian.org.
RUN sed -i \
      -e 's|^deb http://deb\.debian\.org|# deb http://deb.debian.org|' \
      -e 's|^# deb http://snapshot\.debian\.org|deb http://snapshot.debian.org|' \
      /etc/apt/sources.list && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/no-check-valid-until

# Install system dependencies, then clean up
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    # these are our own dependencies and utilities
    apt-get install --yes --no-install-recommends \
      net-tools \
      procps \
      tini && \
    # these are ckan dependencies, as reported in the ckan Dockerfile
    apt-get install --yes --no-install-recommends \
      libmagic1 \
      libpq-dev \
      libxml2-dev \
      libxslt-dev \
      libgeos-dev \
      libssl-dev \
      libffi-dev \
      postgresql-client \
      build-essential \
      git-core \
      wget \
      curl && \
    # these are ckanext-spatial dependencies \
    apt-get install --yes --no-install-recommends \
      proj-bin \
      python3-dev \
      libxslt1-dev \
      libgeos-c1v5  \
      libgdal-dev \
      zlib1g-dev && \
    apt-get --yes clean && \
    rm -rf /var/lib/apt/lists/*

# download poetry

RUN curl --silent --show-error --location \
    https://install.python-poetry.org > /opt/install-poetry.py


# Create a normal non-root user so that we can use it to run
RUN useradd --create-home appuser

# Compile python stuff to bytecode to improve startup times
RUN python -c "import compileall; compileall.compile_path(maxlevels=10)"

USER appuser

RUN mkdir /home/appuser/app  && \
    mkdir /home/appuser/data && \
    python opt/install-poetry.py --yes --version 1.4.2

ENV PATH="$PATH:/home/appuser/.local/bin" \
    # This allows us to get traces whenever some C code segfaults
    PYTHONFAULTHANDLER=1 \
    CKAN_INI=/home/appuser/ckan.ini

WORKDIR /home/appuser/app
COPY --chown=appuser:appuser pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main --no-interaction --no-ansi
COPY --chown=appuser:appuser . .

EXPOSE 5000

# Now install our code
COPY --chown=appuser:appuser . .
RUN poetry install --only main
RUN cp -r /home/appuser/app/ckanext/* "$(poetry env info -p)/lib/$(python3 -c 'import sys; print(f"python{sys.version_info.major}.{sys.version_info.minor}")')/site-packages/ckanext/"

# Write git commit identifier into the image
ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT
RUN echo $GIT_COMMIT > /home/appuser/git-commit.txt


# Compile python stuff to bytecode to improve startup times
RUN poetry run python -c "import compileall; compileall.compile_path(maxlevels=10)"

# use tini as the init process
ENTRYPOINT ["tini", "-g", "--", "poetry", "run", "docker_entrypoint"]

CMD ["launch-gunicorn"]