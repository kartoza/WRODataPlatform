FROM python:3.9-slim-bullseye

# Install security updates and system dependencies, then clean up
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get --yes upgrade && \
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
      python-dev \
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
    CKAN_INI=/home/appuser/ckan.ini \
    # Poetry's default 15s HTTP timeout is too short once ~10 concurrent
    # downloads are competing for bandwidth and a big wheel (pandas, scipy,
    # xarray, ...) is in flight, causing spurious ReadTimeoutError/
    # ConnectionError failures during `poetry install`.
    POETRY_REQUESTS_TIMEOUT=120

# setuptools 82.0.0 (2026-02-08) removed pkg_resources entirely. CKAN
# ckan-2.9.11's own setup.py (its last 2.9.x release, so there's no
# upstream fix) still does `from pkg_resources import parse_version`.
# Poetry always fetches the newest setuptools for the throwaway venv it
# builds git dependencies in, regardless of any pin in our pyproject.toml,
# so we restore just enough of pkg_resources via PYTHONPATH, which every
# build subprocess poetry spawns inherits. This must NOT be a persistent
# ENV: the real, complete pkg_resources (from the main venv's setuptools,
# pinned well below 82 in poetry.lock) is needed at runtime by CKAN's
# plugin loader (ckan.plugins.core uses pkg_resources.iter_entry_points),
# and our stub only implements parse_version, so it must only shadow
# pkg_resources during these two build-time `poetry install` invocations.
RUN mkdir -p /home/appuser/pkg_resources_shim && \
    printf 'from distutils.version import LooseVersion as parse_version\n' \
      > /home/appuser/pkg_resources_shim/pkg_resources.py

WORKDIR /home/appuser/app
COPY --chown=appuser:appuser pyproject.toml poetry.lock ./
RUN PYTHONPATH=/home/appuser/pkg_resources_shim \
    poetry install --no-root --only main --no-interaction --no-ansi
COPY --chown=appuser:appuser . .

EXPOSE 5000

# Now install our code
COPY --chown=appuser:appuser . .
RUN PYTHONPATH=/home/appuser/pkg_resources_shim poetry install --only main
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