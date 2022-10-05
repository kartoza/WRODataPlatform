import ckan.plugins.toolkit as toolkit
from ckan.common import config
import ckan.logic as logic
import os
import pathlib
from .actions_helpers import *
import ckan.lib.uploader as uploader
from ...gcs_functions import delete_blob
from ckan.lib.helpers import flash_notice, redirect_to, full_current_url
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
    wro_theme = "" if data_dict.get('wro_theme') is None else data_dict.get('wro_theme')
    data_structure_category = "" if data_dict.get('data_structure_category') is None else data_dict.get('data_structure_category')
    uploader_estimation_of_extent = "" if data_dict.get('uploader_estimation_of_extent_of_processing') is None else data_dict.get('uploader_estimation_of_extent_of_processing')
    data_classification = "" if data_dict.get('data_classification') is None else data_dict.get('data_classification')

    # handle the case where one of the above is missing.
    # flash an error

    cloud_path = os.path.join(wro_theme,data_structure_category,uploader_estimation_of_extent,data_classification)
    cloud_path = cloud_path.title()
    extras = data_dict.get("extras")
    if extras is None:
        data_dict["extras"] = []
    data_dict['extras'].append({"key":"cloud_path", "value":cloud_path})
    result = original_action(context, data_dict) if access else None
    return result

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
    if data_dict.get("is_link") is True or data_dict.get("is_bigquery_table") is True:
        updated_resource = original_action(context, data_dict) if access else None
        add_view_to_model(context, package, updated_resource)
        return updated_resource

    # ============== cloud path
    resource_cloud_path = get_cloud_path(package)
    if resource_cloud_path == "":
        flash_notice("No cloud path provided the package, please update the package, empty resource is created!")
        return
    logger.debug("cloud path from resource create:", resource_cloud_path)
    # ============== create the resource
    updated_resource = original_action(context, data_dict) if access else None
    
    resource_name = data_dict.get("name")    # this name is file name not the name of the resource provided in the form
    if resource_name is None or resource_name is "":
        flash_notice(f"No file provided, empty resource has been created !")
        return

    res_id = updated_resource.get("id")
    full_name = cloud_url_resource_name(data_dict, updated_resource)
    if full_name =="":
        flash_notice("not path provided for the cloud resource, empty resource is create")
        return

    container_name = config.get('container_name')
    model = context["model"]

    # ============ is it created in gcs
    if get_url_from_gcs_resource(data_dict, updated_resource) == "true":
        full_url = 'https://storage.cloud.google.com/'+container_name+'/'+full_name
    else:
        full_url = 'https://storage.cloud.google.com/'+container_name+'/'+resource_cloud_path+'/'+ pkg_name + "/" + full_name
    
    # ============ commit to the database
    full_url = full_url.lower()
    logger.debug("full resource url:", full_url)
    if data_dict.get("is_link") is None or data_dict.get("is_link") is False:
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
            updated_resource['mimetype'] = upload.mimetype

    if 'size' not in updated_resource:
        if hasattr(upload, 'filesize'):
            updated_resource['size'] = upload.filesize

    upload.upload(updated_resource, uploader.get_max_resource_size())


def add_view_to_model(context, package, updated_resource):
    toolkit.get_action('resource_create_default_resource_views')(
    {'model': context['model'], 'user': context['user'],
    'ignore_auth': True},
    {'package': package,
    'resource': updated_resource})

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
    for item in package_extras:
        if item.get("key") == "cloud_path":
            cloud_path = item.get("value")
    # if resource.get("is_link") is None or resource.get("is_link") is False:
    #     if resource.get("is_bigquery_table") is None or resource.get("is_bigquery_table") is False:
    #         delete_blob(package_name,cloud_path,resource)
    
    original_action(context, data_dict)