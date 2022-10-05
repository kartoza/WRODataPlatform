import pytest
import sys
from pathlib import Path
import requests

@pytest.fixture
def resource():
    return {'bucket': 'wrc_wro_datasets', 'contentType': 'image/png', 'crc32c': '6OtRBw==', 'etag': 'CNi4t97nyPoCEAE=',
            'generation': '1664963329252440',
            'id': 'wrc_wro_datasets/agriculture/structured/refined/time series/130-211-222-159-metadata-form-heeet-maize-northern-cape-2012/data for manuscript/cloud_logo.png/1664963329252440',
            'kind': 'storage#object', 'md5Hash': 'MPmy+5e4ZJjyx2dwnvGKcA==',
            'mediaLink': 'https://storage.googleapis.com/download/storage/v1/b/wrc_wro_datasets/o/agriculture%2Fstructured%2Frefined%2Ftime%20series%2F130-211-222-159-metadata-form-heeet-maize-northern-cape-2012%2Fdata%20for%20manuscript%2Fcloud_logo.png?generation=1664963329252440&alt=media',
            'metageneration': '1',
            'name': 'agriculture/structured/refined/time series/130-211-222-159-metadata-form-heeet-maize-northern-cape-2012/data for manuscript/cloud_logo.png',
            'selfLink': 'https://www.googleapis.com/storage/v1/b/wrc_wro_datasets/o/agriculture%2Fstructured%2Frefined%2Ftime%20series%2F130-211-222-159-metadata-form-heeet-maize-northern-cape-2012%2Fdata%20for%20manuscript%2Fcloud_logo.png',
            'size': '1992', 'storageClass': 'STANDARD', 'timeCreated': '2022-10-05T09:48:49.346Z', 'timeStorageClassUpdated': '2022-10-05T09:48:49.346Z', 'updated': '2022-10-05T09:48:49.346Z'}


@pytest.fixture
def auth():
    return {"Authorization":"6d5f1cf7-6d42-467f-b27f-b0a8454572c0"}

def test_create_cloud_resource(resource, auth):
    """
    the case where resource is 
    created in the cloud and 
    not via CKAN
    """
    #res = {"package_id":package_name,"name":res_short_name, "format":res_format, "created_in_gcs":True, "gcs_full_name":gcs_full_name}
    resource_name = resource['name']
    resource_short_name = get_resource_short_name(resource_name)
    res = {
        "package_id":"130-211-222-159-metadata-form-heeet-maize-northern-cape-2012",
        "name":resource_short_name,
        "format":"csv",
        "url":"",
        "resource_type":"",
        "created_in_gcs":"true", "gcs_full_name":resource_name
    }
    #res = {"package_id":"package_name", "name":resource_name, "created_in_gcs":"true", "gcs_full_name":resource_name}
    response = requests.post("http://localhost/api/3/action/resource_create", headers=auth, data=res)
    created_resource = response.json().get("result")
    res_url = get_resource_url(created_resource)

def get_resource_url(resource):
    resource_id = resource.get("id")
    name = resource.get("gcs_full_name")
    cloud_path, resource_name_and_ext = name.rsplit("/",1)
    resource_name = Path(resource_name_and_ext).stem
    resource_ext = Path(resource_name_and_ext).suffix
    format = resource.get("format")
    full_name = resource_name+"_id_"+resource_id+"."+format
    pkg_name = "130-211-222-159-metadata-form-heeet-maize-northern-cape-2012"
    resource_url = f"https://storage.cloud.google.com/wrc_wro_test/agriculture/structured/refined/time series/{pkg_name}/{full_name}"
    return resource_url

    #full_url = 'https://storage.cloud.google.com/'+container_name+'/'+resource_cloud_path+'/'+ pkg_name + "/" + full_name


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