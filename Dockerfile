# See CKAN docs on installation from Docker Compose on usage
FROM python:3.8-slim
#FROM brunneis/python:3.8.3-ubuntu-20.04
# if you didn't include this, ubuntu will ask you about locale and these things.
ENV DEBIAN_FRONTEND noninteractive

# Install required system packages
RUN apt-get -q -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get -q -y upgrade \
    && apt-get -q -y install --no-install-recommends\
        python-dev \
        python3-dev \
        python3-pip \
        python3-wheel \
        postgresql-client \
        libpq-dev \
        libxml2-dev \
        libxslt-dev \
        libgeos-dev \
        libssl-dev \
        libffi-dev \
        libmagic1 \
        build-essential \
        postgresql-client \
        git-core \
        wget \
        git-core \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

#Define environment variables
ENV CKAN_HOME /home/wro
#ENV CKAN_VENV $CKAN_HOME/venv
ENV CKAN_CONFIG /etc/ckan
ENV CKAN_STORAGE_PATH=/var/lib/ckan
# create these directories
RUN mkdir -p $CKAN_HOME $CKAN_CONFIG $CKAN_STORAGE_PATH
WORKDIR $CKAN_HOME
RUN chmod -R 777 $CKAN_CONFIG
COPY ./ckan.ini $CKAN_CONFIG
RUN python3 -m venv . && . bin/activate \
# there is an error with ckan setuptools, and flask-debugtoolbar version and gunicorn
&& pip install setuptools==45 && pip install flask-debugtoolbar && pip install gunicorn\
# install ckan and the extensions (use root pip, we don't need venv)
# todo (use poetry)
&& pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.9.5#egg=ckan[requirements]'

RUN ln -s $CKAN_HOME/src/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini
RUN ls $CKAN_HOME
RUN ls $CKAN_CONFIG
RUN . bin/activate && ckan -c $CKAN_CONFIG/ckan.ini db init
# setup gunicorn instead of the development server

CMD ["ckan","-c","/etc/ckan/ckan.ini", "run", "--host", "0.0.0.0"]
