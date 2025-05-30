# wro-Portal
The wro Portal has been proposed as a system of software components functioning together as the national central earth observation geospatial repository, with a view to metadata and open geospatial API standards compliance as well as user impact maximization 

# Documentation:
Preliminary documentation for the SAOSS-Portal can be accessed [here](https://kartoza.github.io/wro-Portal/about/). The documentation is still a WIP and will be updated on a regular basis as the platform is being developed.

# Deployment
This project is deployed onto following environment:

- Testing: TBD
- Staging: TBD
- Production: TBD

# Quick Installation Guide
This project is a [ckan](https://ckan.org/) extension, it can be installed standalone. To deploy this project we use  [docker,](http://docker.com/) so you need to have docker running on the host.

Clone the source cose
```
git clone https://github.com/kartoza/WRODataPlatform.git
```

#### Build docker images

```
cd WRODataPlatform/docker
./build.sh
```

Start up the project

```
./compose.py --compose-file docker-compose.yml --compose-file docker-compose.dev.yml up
```

Run down the project 

```
./compose.py --compose-file docker-compose.yml --compose-file docker-compose.dev.yml down
```

#### Initialize CKAN database

The first time you launch it you will need to set up the ckan database (since
the ckan image's entrypoint explicitly does not take care of this, as
mentioned above). Run the following command:

```
docker exec -ti wro-ckan-web-1 poetry run ckan db init
```

Afterwards, proceed to run any migrations required by the ckanext-wro extension

```
docker exec -ti wro-ckan-web-1 poetry run ckan db upgrade --plugin wro
```

Now you should be able to go to `http://localhost:5000` and see the ckan
landing page. If not, you may need to reload the ckan web app after
performing the DB initialization step. This can done by sending the `HUP`
signal to the gunicorn application server (which is running our ckan
flask app):

```
docker exec -ti wro-ckan-web-1 bash -c 'kill -HUP 1'
```

#### Create sysadmin user

After having initialized the database you can now create the first CKAN
sysadmin user.

```
docker exec -ti wro-ckan-web-1 poetry run ckan sysadmin add admin
```

Answer the prompts in order to provide the details for this new user.
After its successful creation you can login to the CKAN site with the `admin`
user.


After starting up, the project is available on your local host at http://localhost:5000 


## Operations

#### Rebuild solr index

```
# check if there are any datasets that are not indexed
ckan search-index check

# re-index
docker exec -it wro-ckan-web-1 poetry run ckan search-index rebuild
```


#### Operate harvesters

You may use the various `ckan harvester <command>` commands to operate existing
harvesters

Create a job:

```
docker exec -t wro-ckan_harvesting-runner poetry run ckan harvester job <source-id>
```

#### Send notifications by email

This needs to be run periodically (once per hour is likely enough).

```
docker exec -it wro-ckan-web-1 ckan wro send-email-notifications
```

Additionally, in order for notifications to work, there is some configuration:

- The CKAN settings must have `ckan.activity_streams_email_notifications = true`
- The CKAN settings must have the relevant email configuration (likely being passed
  as environment variables)
- Each user must manually choose to receive notification e-mails - This is done in
  the user's profile
- Each user must manually follow those entities (datasets, organizations, etc) that
  it finds interesting enough in order to be notified of changes via email

#### Refresh pycsw materialized view

This needs to be run periodically (once per hour is likely enough).

```
docker exec -ti wro-ckan-web-1 poetry run ckan wro pycsw refresh-materialized-view
```

#### Generate pycsw DB view

In order to be able to serve the system's datasets through various OGC standards, create a DB materialized view
in order to integrate with pycsw:

```bash
docker exec -ti wro-ckan-web-1 poetry run ckan wro pycsw create-materialized-view
```
