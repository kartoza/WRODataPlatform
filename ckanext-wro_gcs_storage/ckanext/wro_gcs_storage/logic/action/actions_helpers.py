import ckan.plugins.toolkit as toolkit
import pathlib
import json
import ckan.logic as logic
from ckan.lib.dictization.model_dictize import resource_dictize
import ckan.model as model
_get_or_bust = logic.get_or_bust
import logging

logger = logging.getLogger(__name__)

def is_resource_link(data_dict: dict):
    """
        defines if the resource is an uploaded file or an external link
        and adds is_link attribute to the data dictionary.
        follows the same ckan logic differentiating links and uploaded
        files (https://github.com/ckan/ckan/blob/master/ckan/lib/uploader.py#L167).

        args:
        -----
            data_dict[dict]: holds the resource data.
    
    """
    logger.debug("is resource link action helper:", 
        "resource name:", data_dict.get("name"),
        "resource url:", data_dict.get("url"),
    )
    url = data_dict.get('url')
    if url is not None:
        starts_with_http = url.startswith('http')
        data_dict['is_link'] = starts_with_http
        data_dict["original_url"] = data_dict.get("url")
    return data_dict
    
def is_resource_bigquery_table(data_dict: dict):
    """
        check if the resource is a bigquery file,
        with the wro the bigquery files don't have
        neither a url nor an upload file.
    """
    if data_dict.get('is_link') is None or data_dict.get('is_link') == False:
        bigquery_formats = ["bq", "bigquery", "big query", "big_query"]
        incoming_format = data_dict.get('format')
        if incoming_format is None:
            name = data_dict.get("name")
            if name is not None:
                incoming_format = pathlib.Path(name).suffix
                incoming_format = incoming_format.lower()
        if any(string in incoming_format for string in bigquery_formats):
            incoming_format = incoming_format.lower()
            data_dict["is_bigquery_table"] = True
            # when making a resource create from the api
            # resource_name might not be given but the url
            # might, or might not.
            data_dict["name"] = data_dict["resource_name"]
        else:
            data_dict["is_bigquery_table"] = False
    
    else:
        data_dict["is_bigquery_table"] = False        
    
    return data_dict



def get_resource_package(data_dict, context):
    """
    get resource package
    """
    package_id = _get_or_bust(data_dict, 'package_id')
    package = toolkit.get_action("package_show")(dict(context, return_type='dict'),{'id': package_id})
    return package


def get_cloud_path(package):
    """
    get cloud path
    from the package extras
    """
    resource_cloud_path = ""
    
    package_extras = package.get("extras")   
    # if package extras is None cloud path will flash a message
    if package_extras is not None:
        for item in package_extras:
            if item.get("key") == "cloud_path":
                resource_cloud_path = item.get("value")
    else:
        return ""

    if resource_cloud_path is None:
        return ""
    return resource_cloud_path

def check_path_structure(resource_name):
    """
    we need to neglect the paths
    that don't follow something as
    wro_theme/data_structure_category/uploader_estimation_of_extent/data_classification/package_name/..
    """
    if resource_name is None:
        return False

    packages_names = toolkit.get_action("package_list")()
    resource_name_split = resource_name.split("/",5)
    resource_package_name = resource_name_split[4]
    if resource_package_name not in packages_names:
        return False
    else:
        return True


def cloud_url_resource_name(resource, updated_resource):
    if resource_created_in_gcs(resource) == "true":
        return get_url_from_gcs_resource(resource, updated_resource)
    else:
        resource_name = resource.get("name")
        name = pathlib.Path(resource_name).stem
        name = lower_underscore_resource_name(name)
        ext = pathlib.Path(resource_name).suffix
        res_id = updated_resource.get("id")
        full_name = name + '_id_'+ res_id + ext
        full_name = full_name.lower()    
        return full_name

def lower_underscore_resource_name(name):
    name = name.lower()
    name = name.replace(" ", "_")
    return name

def resource_created_in_gcs(data_dict:dict):
    """
    check whether the resource
    is create in gcs, if so we
    beed to create the path 
    from the reosurce name
    """
    created_in_gcs = data_dict.get("created_in_gcs") # assuming it's called name
    if created_in_gcs is None or created_in_gcs is False:
        return False
    else:
        return created_in_gcs

def get_url_from_gcs_resource(resource, updated_resource):
    """
    the case where is the 
    resource is not in CKAN
    """
    name = resource.get("gcs_full_name")
    if name is None:
        return ""
    cloud_path, resource_name_and_ext = name.rsplit("/",1)
    resource_name = pathlib.Path(resource_name_and_ext).stem
    resource_ext = pathlib.Path(resource_name_and_ext).suffix

    id = updated_resource.get("id")
    if id is None:
        return ""
    resource_name_id = resource_name + "_id_" + id
    full_name =  cloud_path + "/" + resource_name_id + resource_ext
    logger.debug("name of resource created in the cloud first:", full_name)
    return full_name   