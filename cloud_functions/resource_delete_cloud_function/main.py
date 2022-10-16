"""
reflect changes with gcs files in CKAN
"""
import functions_framework
import requests
from google.cloud import storage

@functions_framework.cloud_event
def ckan_gcs_resource_delete(cloud_event):
    """
    a function that is required to have
    cloud event object as a param 
    """
    data = cloud_event.data
    print(data)
    headers = {"Authorization":"6d5f1cf7-6d42-467f-b27f-b0a8454572c0"}
    if data is not None:
        resource_name = data.get("name")
        metadata = data.get("metadata")
    if resource_name:
        res_id = get_resource_id(resource_name, metadata)
        print("resource extracted id:",res_id)
        res = {"id":res_id}
        response = requests.post("https://data.waterresearchobservatory.org/api/3/action/resource_delete",headers=headers, data=res)

def get_resource_id(res_name:str, metadata):
    """
    extract the resource name, id and extension
    the resource name would be without
    the cloud path part
    e.g. 
    Agriculture/Structured/Access/Time Series/Package id/resource_name_id_0f203d.csv
    -> resource_name
    """
    id = ""
    if '_id_' in res_name:
        first_part, last_part = res_name.rsplit("/",1)
        resource_name, id = last_part.split("_id_", 1)
        id, ext = id.split(".")
    else:
        try:
            print(metadata)
            if metadata is not None:
                ckan_res_id = metadata.get("ckan_resource_id")
                print("res_id:",ckan_res_id)
                if ckan_res_id is not None:
                    id = ckan_res_id
        except:
            pass
    return id