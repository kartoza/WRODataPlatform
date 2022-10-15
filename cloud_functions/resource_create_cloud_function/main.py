"""
reflect changes with gcs files in CKAN
"""
from ast import Str
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
    headers = {"Authorization":"6d5f1cf7-6d42-467f-b27f-b0a8454572c0"}
    resource_name = ""
    if data is not None:
        resource_name = data.get("name")
    else:
        return
    
    if "_id_" not in resource_name: # TODO: use regex for id pattern
        client = storage.Client()
        bucket = client.bucket("wrc_wro_datasets")
        blob = bucket.get_blob(resource_name)

        blob_metadata = blob.metadata
        package_id = ""
        send_to_bigquery = ''
        created_via_ckan = ''
        if blob_metadata is not None:
            package_id = blob_metadata.package_id
            send_to_bigquery = blob_metadata.bigquery_file
            created_via_ckan = blob_metadata.created_via_ckan
        if created_via_ckan == "true":
            return

        package_name = get_package_name(resource_name, headers)
        if package_name == "":
            print(f"this resource: \"{resource_name}\" seems to not have a package, wasn't referenced by CKAN")
            return

        res_format = get_resource_format(resource_name)
        res_short_name = get_resource_short_name(resource_name)
        gcs_full_name = data.get("name")
        res = {"package_id":package_name,"name":res_short_name, "format":res_format, "created_in_gcs":"true", "gcs_full_name":gcs_full_name}
        try:
            response = requests.post("https://data.waterresearchobservatory.org/api/3/action/resource_create",headers=headers, data=res)
            response_ob = response.json()
        except:
            print("couldn't create ckan resource, post request failed")
            return 
        response_result = response_ob.get("result")
        resource_ckan_id = response_result.get("id")
        resource_ckan_url = construct_uploaded_resource_url(resource_name)
        patched_resource = {"id":resource_ckan_id, "url":resource_ckan_url}
        response = requests.post("https://data.waterresearchobservatory.org/api/3/action/resource_patch",headers=headers, data=patched_resource)

        # response_result = response_ob.get("result")
        # if response_result is not None:
        #     resource_ckan_id = response_result.get("id")
        #     resource_ckan_url = response_result.get("url") if response_result is not None else ""
        #     # the following also calls rename_bucket_blob
        #     underscord_resource_names = get_resource_underscored_url(resource_ckan_url)
        #     resource_ckan_url = underscord_resource_names.get("updated_url")
        #     patched_resource = {"id":resource_ckan_id, "url":resource_ckan_url}
        #     response = requests.post("https://data.waterresearchobservatory.org/api/3/action/resource_patch",headers=headers, data=patched_resource)
        #     new_blob_name = underscord_resource_names.get("new_blob_name")
        #     bucket.rename_blob(blob, new_blob_name)
    

def get_package_name(res_name:str, auth:dict)-> str:
    """
    packages names are unique 
    """
    slash_count = res_name.count("/")
    if slash_count < 5:
        return ""

    response = requests.post("https://data.waterresearchobservatory.org/api/3/action/package_list", headers=auth)
    res_ob = response.json()
    packages = res_ob.get("result")
    
    first_part = res_name.split("/",5)
    package_name = first_part[4]
    
    if package_name not in packages:
        return ""

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
    return Path(last_part).stem

# def get_resource_underscored_url(res_url:str, bucket_name="wrc_wro_datasets") -> dict:
#     """
#     extract the resource name, id and extension
#     the resource name would be without
#     the cloud path part
#     e.g. 
#     Agriculture/Structured/Access/Time Series/Package id/resource_name_id_0f203d.csv
#     -> resource_name
#     """
#     first_part, last_part = res_url.rsplit("/",1)
#     resource_name, id_with_ext = last_part.split("_id_", 1)
#     res_short_name = resource_name.replace(" ","_")
#     name_with_id = res_short_name+"_id_"+id_with_ext
#     updated_url = first_part+"/"+ name_with_id
#     removed_domain = remove_url_domain(first_part, bucket_name)
#     new_blob_name = removed_domain  + "/" + name_with_id
#     return {"updated_url":updated_url, "new_blob_name":new_blob_name}


def construct_uploaded_resource_url(resource_name:str):
    """
    returns the borwser authenticated borwser url of the
    resource, https://cloud.google.com/storage/docs/request-endpoints#cookieauth
    """
    return f"https://storage.cloud.google.com/wrc_wro_datasets/{resource_name}"

def get_resource_format(resource_name):
    ext = Path(resource_name).suffix
    return ext[1:]


def remove_url_domain(resource_url:str, bucket_name="wrc_wro_datasets"):
    """
    removes storage.google.com
    from the path
    """
    new_name = resource_url.replace(f"https://storage.cloud.google.com/{bucket_name}/","")
    return new_name