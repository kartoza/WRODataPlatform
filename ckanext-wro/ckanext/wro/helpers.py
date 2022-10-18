import json
import logging
import typing
from shapely import geometry
import pandas as pd
from ckan.plugins import toolkit
from ckan import model
import json
from ckan.common import config
from google.cloud import storage
import gcsfs
from io import BytesIO, StringIO


logger = logging.getLogger(__name__)

def get_default_spatial_search_extent(
    padding_degrees: typing.Optional[float] = None,
) -> typing.Dict:
    """
    Return GeoJSON polygon with bbox to use for default view of spatial search map widget.
    """
    configured_extent = toolkit.config.get(
        "ckan.dalrrd_emc_dcpr.default_spatial_search_extent"
    )
    if padding_degrees and configured_extent:
        parsed_extent = json.loads(configured_extent)
        result = _pad_geospatial_extent(parsed_extent, padding_degrees)
    else:
        result = configured_extent
    return result


def get_default_bounding_box() -> typing.Optional[typing.List[float]]:
    """Return the default bounding box in the form upper left, lower right
    This function calculates the default bounding box from the
    `ckan.dalrrd_emc_dcpr.default_spatial_search_extent` configuration value. Note that
    this configuration value is expected to be in GeoJSON format and in GeoJSON,
    coordinate pairs take the form `lon, lat`.
    This function outputs a list with upper left latitude, upper left latitude, lower
    right latitude, lower right longitude.
    """

    configured_extent = toolkit.config.get(
        "default_spatial_search_extent"
    )
    #parsed_extent = json.loads(configured_extent)
    return convert_geojson_to_bbox(configured_extent)
    
def convert_geojson_to_bbox(
    geojson: typing.Dict,
) -> typing.Optional[typing.List[float]]:
    try:
        geojson = json.loads(geojson)
        coords = geojson["coordinates"][0]
    except:
        result = None
    else:
        min_lon = min(c[0] for c in coords)
        max_lon = max(c[0] for c in coords)
        min_lat = min(c[1] for c in coords)
        max_lat = max(c[1] for c in coords)
        result = [max_lat, min_lon, min_lat, max_lon]
    return result

def _pad_geospatial_extent(extent: typing.Dict, padding: float) -> typing.Dict:
    geom = geometry.shape(extent)
    padded = geom.buffer(padding, join_style=geometry.JOIN_STYLE.mitre)
    oriented_padded = geometry.polygon.orient(padded)
    return geometry.mapping(oriented_padded)


def get_bigquery_table_name(resource):
    """
    when a bigquery table is given,
    there is no name in the packge
    resources list, we need to 
    retrive the table name and provide
    it in the package resources_info
    """
    if resource["is_bigquery_table"] == True:
        resource["name"] = resource["resource_name"]
        return resource["resource_name"] 
    return ""
    

def get_package_name(package_id:str)-> str: 
    """
    get the package name from the id,
    it's useful while retrieving packages
    from resources.
    """
    package_show_action = toolkit.get_action("package_show")
    package_name = package_show_action(data_dict={"id":package_id})["title"]
    return package_name


def resource_read_helper(data_dict:dict):
    # the problem with the current view is that is the resource
    # provided is not the last updated one, get the resouce and pass it
    q = f""" select url from resource where id='{data_dict["id"]}' """
    session_res = []
    query_res = model.Session.execute(q)
    for item in query_res:
        session_res.append(item)
    
    cloud_path = session_res[0][0]
    return change_spaces_to_underscores(cloud_path)

def change_spaces_to_underscores(name:str):
    """
    as the buckets changes spaces
    int the name of resource to
    dashes, we need to hcange this
    here after we grab from database
    note that the uploader do this so what
    we have in the bucket has underscores in
    the name, but the database has spaces. 
    """
    # get the last part after the last / 
    if 'https://storage.cloud.google.com/' in name:
        first_part, last_part = name.rsplit("/",1)
        res_name, res_id = last_part.split("_id_")
        res_name = res_name.replace(" ","_")
        name = first_part+"/"+res_name+"_id_"+res_id
        name = name.lower()
    return name


def parse_cloud_csv_data(url:str):
    """
    get csv data from url
    and parse it via
    pandas
    """
    url = url.replace(" ", "%20")
    blob_s = _get_blob("weather_and_climate_data/structured/access/time series/50-years-of-daily-hydroclimatic-data-per-quaternary-catchment-in-south-africa-1950-1999/annual_enterprise_survey_2021_financial_year_provisional_csv_id_0f9a1f20-1d85-474a-9080-beb606631eae.csv")
    #fs = gcsfs.GCSFileSystem(project='wrc-wro', token=service_account_path)
    # with fs.open('wrc_wro_datasets/agriculture/structured/refined/time%20series/maize-long-term-trial/long_term_trial_datasets_id_6603b69c-53f2-43f7-9574-97c67206ec56.xlsx') as f:
    #     csv_ob =  pd.read_csv(f)
    
    #csv_ob = pd.read_excel(url, storage_options={"token":service_account_path})
    #csv_ob = dd.read_csv(url, storage_options={"token":service_account_path}, encoding="latin-1")
    #raise RuntimeError(url)
    #csv_ob = pd.read_csv(url, error_bad_lines=False)
    # blob_s = StringIO(blob_s)
    csv_ob =  pd.read_csv(blob_s)
    return csv_ob


def _get_blob(blob_name:str):
    """
    gets blob object with `blob_name`
    from a bucket
    """
    service_account_path = config.get('service_account_path')
    client = storage.Client.from_service_account_json(service_account_path)
    bucket = client.bucket("wrc_wro_datasets")
    blob = bucket.get_blob(blob_name)
    byte_stream = BytesIO()
    #string = blob.download_to_file(byte_stream)
    if blob is not None:
        blob.download_to_file(byte_stream)
        byte_stream.seek(0)
        return byte_stream

def get_packages_count():
    """
    returns the number 
    of packages in the site
    """
    packages_list_count = len(toolkit.get_action("package_list")({}, {}))
    return packages_list_count

def get_organizations_count():
    """
    returns the organizations
    count
    """
    orgs_list_count = len(toolkit.get_action("organization_list")({}, {}))
    return orgs_list_count
