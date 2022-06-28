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

    RUN useradd --create-home appuser

    USER appuser

    RUN mkdir /home/appuser/app  && mkdir /home/appuser/data && mkdir /home/appuser/ckan_storage

    ENV PATH="$PATH:/home/appuser/.local/bin"

    ENV CKAN_INI /home/appuser/app/ckan.ini

    ENV PYTHONFAULTHANDLER=1 

    WORKDIR /home/appuser/app

    COPY --chown=appuser:appuser requirements.txt ./

    RUN pip install -e git+https://github.com/ckan/ckan.git@ckan-2.9.5#egg=ckan

    RUN pip install -r requirements.txt

    RUN chmod 777 /home/appuser/app/src/ckan/ckan/config/who.ini
    
    RUN ln -s /home/appuser/app/src/ckan/ckan/config/who.ini /home/appuser/app/who.ini

    COPY --chown=appuser:appuser ckan.ini ./

    RUN chmod 777 -R /home/appuser/app/src/ckan/

    COPY --chown=appuser:appuser docker_entry.py ckan.ini ./
    

EXPOSE 5000

# copy the dynamic parts (our extension) to the working direcotry
# COPY . .

# install the extension and it's req with poetry
#RUN poetry install --no-dev

ENTRYPOINT ["tini", "-g", "--"]

CMD ["python", "docker_entry.py", "gunicorn-up"]
