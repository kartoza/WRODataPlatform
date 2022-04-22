# See CKAN docs on installation from Docker Compose on usage
FROM python:3.8-slim-bullseye

# Install required system packages -- this is coming from ckan dockerfile
RUN apt-get -q -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get -q -y upgrade \
    && apt-get -q -y install \
        python-dev \
        python-pip \
        python-virtualenv \
        python-wheel \
        python3-dev \
        python3-pip \
        python3-virtualenv \
        python3-wheel \
        libpq-dev \
        libxml2-dev \
        libxslt-dev \
        libgeos-dev \
        libssl-dev \
        libffi-dev \
        postgresql-client \
        build-essential \
        git-core \
        vim \
        wget \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

# ckan spatial dependencies -- this is coming from EMC, needed with the map
RUN   apt-get install --yes --no-install-recommends \
      proj-bin \
      python-dev \
      libxslt1-dev \
      libgeos-c1v5  \
      zlib1g-dev && \
    apt-get --yes clean && \
    rm -rf /var/lib/apt/lists/*

# installing dependencies found in the installation guide and not above
RUN apt-get install --yes \
    postgresql git-core solr-tomcat openjdk-8-jdk redis-server

# out Working directory  
WORKDIR /home/wro

# Define environment variables -- altering ckan default ones
ENV CKAN_HOME $WORKDIR/ckan
ENV CKAN_VENV $WORKDIR
ENV CKAN_CONFIG /etc/ckan/default
# this is the dfault storage path, no need to change it.
ENV CKAN_STORAGE_PATH=/var/lib/ckan

# create those folders
RUN mkdir -p $CKAN_VENV $CKAN_CONFIG $CKAN_STORAGE_PATH && \
    sudo chown -R `whoami` /etc/ckan/

# Build-time variables specified by docker-compose.yml / .env
ARG CKAN_SITE_URL

# Setup virtual environment for CKAN, this command happens inisde WORKDIR
RUN python3 -m venv . &&

# installing dependencies, also happens inisde workdir
COPY requirements.txt . 
RUN pip install -r requirements.txt

# setup ckan
RUN source bin/activate && \
    pip install -e 'git+https://github.com/Mohab25/ckan.git@ckan-2.9.5#egg=ckan[requirements]' && \
    sudo -u postgres createuser -S -D -R -P ckan_default && \
    sudo -u postgres createdb -O ckan_default ckan_default -E utf-8 && \
    ckan generate config /etc/ckan/default/ckan.ini && \
    


# Setup CKAN
ADD . $CKAN_VENV/src/ckan/
RUN ckan-pip install -U pip && \
    ckan-pip install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckan/requirement-setuptools.txt && \
    ckan-pip install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckan/requirements-py2.txt && \
    ckan-pip install -e $CKAN_VENV/src/ckan/ && \
    ln -s $CKAN_VENV/src/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini && \
    cp -v $CKAN_VENV/src/ckan/contrib/docker/ckan-entrypoint.sh /ckan-entrypoint.sh && \
    chmod +x /ckan-entrypoint.sh && \
    chown -R ckan:ckan $CKAN_HOME $CKAN_VENV $CKAN_CONFIG $CKAN_STORAGE_PATH

ENTRYPOINT ["/ckan-entrypoint.sh"]

USER ckan
EXPOSE 5000

CMD ["ckan","-c","/etc/ckan/production.ini", "run", "--host", "0.0.0.0"]
