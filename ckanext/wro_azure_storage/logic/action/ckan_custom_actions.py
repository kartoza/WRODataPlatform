import ckan.plugins.toolkit as toolkit
from ckan.common import config
import ckan.logic as logic
import os
import pathlib
from .actions_helpers import *
import ckan.lib.uploader as uploader
from ...azure_functions import delete_blob
from ckan.lib.helpers import flash_notice, redirect_to, full_current_url
from ckan.common import c
import logging

logger = logging.getLogger(__name__)

@toolkit.chained_action
def package_create(original_action,context:dict, data_dict:dict) -> dict:
    """
    uploading to the cloud requires
    few pathes to be modified,
    intercepting the package create
    action here
    """
    access = toolkit.check_access("package_create", context, data_dict)
    cloud_path = _set_cloud_path(data_dict)
    extras = data_dict.get("extras")
    # raise RuntimeError(data_dict.get("spatial"))
    if extras is None:
        data_dict["extras"] = []
    data_dict['extras'].append({"key":"cloud_path", "value":cloud_path})    
    data_dict['extras'].append({"key":"extra_spatial", "value":data_dict.get("spatial")})    
    result = original_action(context, data_dict) if access else None
    return result

@toolkit.chained_action
def package_update(original_action,context:dict, data_dict:dict) -> dict:
    """
    update the package
    we need to be able to 
    update also the cloud
    path in case the package
    doesn't have one
    """
    if not c.userobj.sysadmin:
        change_on_dataset(data_dict)
    access = toolkit.check_access("package_update", context, data_dict)
    cloud_path = _set_cloud_path(data_dict)
    extras = data_dict.get("extras")
    package_has_cloud_path = False
    if extras is None:
        data_dict["extras"] = []
    if len(data_dict["extras"]) > 0:
        for item in data_dict["extras"]:
            if item.get("key") is not None and item["key"] == "cloud_path":
                item["value"] = cloud_path
                package_has_cloud_path = True

    elif len(data_dict["extras"]) == 0 or package_has_cloud_path==False:
        data_dict['extras'].append({"key":"cloud_path", "value":cloud_path})

    result = original_action(context, data_dict) if access else None
    return result


@toolkit.chained_action
def package_delete(original_action,context:dict, data_dict:dict)->dict:
    """
    we aren't authorizing the user
    to delete packages if not
    system admin
    """
    if not c.userobj.sysadmin:
            toolkit.base.abort(403,toolkit._("Unauthorized to delete this dataset, please consult system admin"))
    access = toolkit.check_access("package_update", context, data_dict)
    result = original_action(context, data_dict) if access else None
    return result

def _set_cloud_path(data_dict:dict)-> str:
    """
    construct cloud path from
    mulitple fields of the
    package
    """
    wro_theme = "" if data_dict.get('wro_theme') is None else data_dict.get('wro_theme')
    data_structure_category = "" if data_dict.get('data_structure_category') is None else data_dict.get('data_structure_category')
    uploader_estimation_of_extent = "" if data_dict.get('uploader_estimation_of_extent_of_processing') is None else data_dict.get('uploader_estimation_of_extent_of_processing')
    data_classification = "" if data_dict.get('data_classification') is None else data_dict.get('data_classification')

    # handle the case where one of the above is missing.
    # flash an error

    cloud_path = os.path.join(wro_theme,data_structure_category,uploader_estimation_of_extent,data_classification)
    return cloud_path.title()

@toolkit.chained_action
def resource_create(original_action,context:dict, data_dict:dict) -> dict:
    """
    adding cloud path to the resource
    """
    # ============== define main structures <package, resource>
    logger.debug("ckan resource create in gcs:", data_dict)
    data_dict = is_resource_link(data_dict)
    data_dict= is_resource_bigquery_table(data_dict)
    access = toolkit.check_access("resource_create", context, data_dict)
    package = get_resource_package(data_dict, context)
    pkg_name = package.get('name')
    
    # ============== handle the bigquery and url cases here
    if data_dict.get("is_link") == True or data_dict.get("is_bigquery_table") == True: 
        updated_resource = original_action(context, data_dict) if access else None
        handle_upload(updated_resource)
        add_view_to_model(context, package, updated_resource)
        if data_dict.get("is_link") == True:
            updated_resource["url_type"] = "link"
        return updated_resource

    # ============== cloud path
    resource_cloud_path = get_cloud_path(package)
    if resource_cloud_path == "":
        flash_notice("No cloud path provided with the dataset, please update the dataset, empty resource is created!")
        return
    logger.debug("cloud path from resource create:", resource_cloud_path)
    resource_cloud_path = resource_cloud_path.lower()
    # ============== create the resource
    updated_resource = original_action(context, data_dict) if access else None
    
    resource_name = data_dict.get("name")    # this name is file name not the name of the resource provided in the form
    if resource_name is None or resource_name == "":
        flash_notice(f"No file provided, empty resource has been created !")
        return

    res_id = updated_resource.get("id")
    full_name = cloud_url_resource_name(data_dict, updated_resource)
    if full_name =="":
        flash_notice("not path provided for the cloud resource, empty resource is create")
        return

    bucket_name = config.get('bucket_name')
    model = context["model"]

    # ============ is it created in gcs
    if resource_created_in_gcs(data_dict) == "true":
        full_url = 'https://storage.cloud.google.com/'+bucket_name+'/'+full_name
    else:
        full_url = 'https://storage.cloud.google.com/'+bucket_name+'/'+resource_cloud_path+'/'+ pkg_name + "/" + full_name
    
    # ============ commit to the database
    full_url = full_url.lower()
    logger.debug("full resource url:", full_url)
    if data_dict.get("is_link") is None or data_dict.get("is_link") == False:
        if data_dict.get("is_bigquery_table") is None or data_dict.get("is_bigquery_table") is False:
            updated_resource = toolkit.get_action("resource_patch")(context, data_dict={"id":res_id,"url":full_url, "url_type":"link"})
            q = f""" update resource set url='{full_url}' where id='{res_id}' """
            model.Session.execute(q)
            model.repo.commit()

    handle_upload(updated_resource)
    add_view_to_model(context, package, updated_resource)    
    
    return updated_resource

def handle_upload(updated_resource):
    """
    handle the uploading part of
    the resource creation
    """
    upload = uploader.get_resource_uploader(updated_resource)
    if 'mimetype' not in updated_resource:
        if hasattr(upload, 'mimetype'):
            updated_resource['mimetype'] = upload.get('mimetype')

    if 'size' not in updated_resource:
        if hasattr(upload, 'filesize'):
            updated_resource['size'] = upload.filesize

    upload.upload(updated_resource, uploader.get_max_resource_size())


def add_view_to_model(context, package, updated_resource):
    result = toolkit.get_action('resource_create_default_resource_views')(
    {'model': context['model'], 'user': context['user'],
    'ignore_auth': True},
    {'package': package,
    'resource': updated_resource})
    logger.debug("resource views created:", result,
                "view create from package:", package,
                "resource is:", updated_resource 
    )
    return result

@toolkit.chained_action
def resource_delete(original_action, context:dict, data_dict:dict) -> dict:
    """
    intercepting resource delete action,
    we are using cloud delete.
    """
    toolkit.check_access('resource_delete', context, data_dict)
    resource = toolkit.get_action("resource_show")(data_dict={"id":data_dict.get("id")})
    package = toolkit.get_action("package_show")(data_dict={"id":resource.get("package_id")})
    package_name = package.get("name")
    package_extras = package.get("extras")
    cloud_path = ""
    if package_extras is not None:
        for item in package_extras:
            if item.get("key") == "cloud_path":
                cloud_path = item.get("value")
        
    if resource.get("is_link") is None or resource.get("is_link") is False:
        if resource.get("is_bigquery_table") is None or resource.get("is_bigquery_table") is False:
            delete_blob(package_name,cloud_path,resource)
    
    original_action(context, data_dict)