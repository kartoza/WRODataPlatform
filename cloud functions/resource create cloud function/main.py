"""
reflect changes with gcs files in CKAN
"""
import functions_framework
from google.cloud import storage
import requests
from pathlib import Path

@functions_framework.cloud_event
def ckan_gcs_resource_create(cloud_event):
    """
    a function that is required to have
    cloud event object as a param 
    """
    data = cloud_event.data
    resource_name = ""
    if data is not None:
        resource_name = data.get("name")
    
    if "_id_" not in resource_name: # TODO: use regex for id pattern
        client = storage.Client()
        bucket = client.bucket("wrc_wro_datasets")
        blob = bucket.get_blob(resource_name)

        blob_metadata = blob.metadata
        if blob_metadata is not None:
            package_id = blob_metadata.package_id
            send_to_bigquery = blob_metadata.bigquery_file

        package_name = get_package_name(resource_name)
        res_format = get_resource_format(resource_name)
        res_short_name = get_resource_short_name(resource_name)
        headers = {"Authorization":"6d5f1cf7-6d42-467f-b27f-b0a8454572c0"}
        res = {"package_id":package_name,"name":res_short_name, "format":res_format}
        response = requests.post("https://data.waterresearchobservatory.org/api/3/action/resource_create",headers=headers, data=res)
        response_ob = response.json()
        print("response object:", response_ob)
        response_result = response_ob.get("result")
        resource_ckan_id = response_result.get("id")
        resource_ckan_url = response_result.get("url") if response_result is not None else ""
        # the following also calls rename_bucket_blob
        underscord_resource_names = get_resource_underscored_url(resource_ckan_url)
        resource_ckan_url = underscord_resource_names.get("")
        patched_resource = {"id":resource_ckan_id, "url":resource_ckan_url}
        response = requests.post("https://data.waterresearchobservatory.org/api/3/action/resource_patch",headers=headers, data=patched_resource)
        new_blob_name = underscord_resource_names.get("new_blob_name")
        bucket.rename_blob(blob, new_blob_name)
    

def get_package_name(res_name:str)-> str:
    """
    packages names are unique 
    """
    first_part, last_part = res_name.rsplit("/",1)
    url_name, package_name = first_part.rsplit("/",1)
    return package_name

def get_resource_short_name(res_name:str) -> dict:
    """
    extract the resource name, id and extension
    the resource name would be without
    the cloud path part
    e.g. 
    Agriculture/Structured/Access/Time Series/Package id/resource_name_id_0f203d.csv
    -> resource_name
    """
    first_part, last_part = res_name.rsplit("/",1)
    #res_name, res_format = last_part.split(".")
    return last_part

def get_resource_underscored_url(res_url:str) -> dict:
    """
    extract the resource name, id and extension
    the resource name would be without
    the cloud path part
    e.g. 
    Agriculture/Structured/Access/Time Series/Package id/resource_name_id_0f203d.csv
    -> resource_name
    """
    first_part, last_part = res_url.rsplit("/",1)
    resource_name, id = last_part.split("_id_", 1)
    res_short_name = resource_name.replace(" ","_")
    name_with_id = res_short_name+"_id_"+id
    updated_url = first_part+"/"+ name_with_id
    new_blob_name = remove_url_domain(first_part) + "/" + name_with_id
    return {"updated_url":updated_url, "new_blob_name":new_blob_name}


def get_resource_format(resource_name):
    return Path(resource_name).suffix

def build_resource_url(res_name:str) -> str:
    """
    build something as:
    https://storage.cloud.google.com/res_name
    which is different that urls returned
    by the event object
    """
    return "https://storage.cloud.google.com/wrc_wro_datasets/"+res_name

def remove_url_domain(resource_url:str):
    """
    removes storage.google.com
    from the path
    """
    return resource_url.replace("https://storage.cloud.google.com/wrc_wro_datasets/","")