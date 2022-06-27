# # See CKAN docs on installation from Docker Compose on usage
FROM python:3.8-slim
# # if you didn't include this, ubuntu will ask you about locale and these things.
ENV DEBIAN_FRONTEND noninteractive

# Install required system packages
RUN apt-get -q -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get -q -y upgrade \
    && apt-get -q -y install --no-install-recommends\
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
      zlib1g-dev && \
    apt-get --yes clean && \
    rm -rf /var/lib/apt/lists/*

# installing poetry section:

    # downloading poetry (different from the usual way as we need to install poetry with 
    #app users instead of root, on how to install poetry https://python-poetry.org/docs/master/#installing-with-the-official-installer)
    
    # =================
    #RUN curl --silent --show-error --location \ 
    #https://install.python-poetry.org > /opt/install-poetry.py
    # =================
    
    # creating a non-root user (requirement by poetry), --create-home creates a home
    # direcotry if not exit (https://manpages.ubuntu.com/manpages/xenial/en/man8/useradd.8.html)
    RUN useradd --create-home appuser

    # set the user to appuser
    USER appuser

    # finally install installing poetry
    
    # =================
    RUN mkdir /home/appuser/app  && mkdir /home/appuser/data
    #    python /opt/install-poetry.py --yes --version 1.1.11
    # =================
    
    # adding the new users to the path (the colon is a separator between folders)
    
    # =================
    ENV PATH="$PATH:/home/appuser/.local/bin"
    # =================

    # adding ckan ini env variable
    ENV CKAN_INI /home/appuser/app/ckan.ini
    # add python default handler to add output fault errors (https://docs.python.org/3/using/cmdline.html#envvar-PYTHONFAULTHANDLER)
    ENV PYTHONFAULTHANDLER=1 
    # setting the working directory
    WORKDIR /home/appuser/app
    # usually poetry begins with empty poetry.lock and 
    # pyproject.toml, but we need to feed the docker container
    # with exsting peotry and pyproject.toml files to take
    # advantage of the docker cache.
    
    # tried peotry but it's really slow, couldn't continue with resolving
    
    # =================
    #COPY --chown=appuser:appuser pyproject.toml poetry.lock ./
    # =================
    
    # getting the dependencies 
    COPY --chown=appuser:appuser requirements.txt ./
    RUN pip install -r requirements.txt


    # to install ckan form git use:
    
    # =================
    # pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.9.5#egg=ckan[requirements]'
    # =================

    ENV cache buster
    # for now just use ckan from local directory
    COPY --chown=appuser:appuser ckan.ini ./ 
    # ownership of directories isn't recursive, contents are not owned
    COPY --chown=appuser:appuser ckan ./ckan/
    RUN chmod 777 /home/appuser/app/ckan/ckan/config/who.ini
    RUN cd ckan && python setup.py develop --user
    RUN ln -s /home/appuser/app/ckan/ckan/config/who.ini /home/appuser/app/who.ini
    # TEMPORARY FOR DEVELOPMENT, putting ckan in the working directory, because
    # for now i don't want to install it from remote to save bandwidth, 
    # in the poetry file it is coming from the same directory that holds
    # poetry.lock and pyproject.toml 
    COPY --chown=appuser:appuser docker_entry.py ckan.ini ./
    # install the dependencies 
    #RUN poetry install --no-root --no-dev

EXPOSE 5000

# copy the dynamic parts (our extension) to the working direcotry
# COPY . .

# install the extension and it's req with poetry
#RUN poetry install --no-dev

# as we have a poetry script called docker_entrypoint (found in the lock file),
# this will run that scrpit which will run click (python package)
# group called cli, then the command line will be ready for another
# command which is launch-gunicorn.

#ENTRYPOINT ["tini", "-g", "--", "poetry", "run", "docker_entrypoint"]
ENTRYPOINT ["tini", "-g", "--"]

CMD ["python", "docker_entry.py", "gunicorn-up"]


# # #Define environment variables
# ENV CKAN_HOME /home/wro
# #ENV CKAN_VENV $CKAN_HOME/venv
# ENV CKAN_CONFIG /etc/ckan
# ENV CKAN_STORAGE_PATH=/var/lib/ckan
# # create these directories
# RUN mkdir -p $CKAN_HOME $CKAN_CONFIG $CKAN_STORAGE_PATH
# WORKDIR $CKAN_HOME
# RUN chmod -R 777 $CKAN_CONFIG
# COPY ./ckan.ini $CKAN_CONFIG
# # RUN python3 -m venv . && . bin/activate \
# # # there is an error with ckan setuptools, and flask-debugtoolbar version and gunicorn
# # && pip install setuptools==45 && pip install flask-debugtoolbar && pip install gunicorn\
# # # install ckan and the extensions (use root pip, we don't need venv)
# # # todo (use poetry)
# # && pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.9.5#egg=ckan[requirements]'

# # RUN ln -s $CKAN_HOME/src/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini
# # RUN ls $CKAN_HOME
# # RUN ls $CKAN_CONFIG
# # RUN . bin/activate && ckan -c $CKAN_CONFIG/ckan.ini db init
# # # setup gunicorn instead of the development server

# # CMD ["ckan","-c","/etc/ckan/ckan.ini", "run", "--host", "0.0.0.0"]
