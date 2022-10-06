import pytest
import sys
from pathlib import Path
import requests
from . import main

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


@pytest.fixture
def ckan_resource(resource):
    resource_name = resource['name']
    resource_short_name = main.get_resource_short_name(resource_name)
    
    res = {
        "package_id":"130-211-222-159-metadata-form-heeet-maize-northern-cape-2012",
        "name":resource_short_name,
        "format":"png",
        "url":"",
        "resource_type":"",
        "created_in_gcs":"true", "gcs_full_name":resource_name
    }

    return res

def test_create_cloud_resource(resource, auth):
    """
    the case where resource is 
    created in the cloud and 
    not via CKAN
    """
    #res = {"package_id":package_name,"name":res_short_name, "format":res_format, "created_in_gcs":True, "gcs_full_name":gcs_full_name}
    resource_name = resource['name']
    package_name = main.get_package_name(resource_name,auth)
    assert package_name != ''
    
    res = {
        "package_id":"130-211-222-159-metadata-form-heeet-maize-northern-cape-2012",
        "name":resource_name,
        "format":"png",
        "url":"",
        "resource_type":"",
        "created_in_gcs":"true", "gcs_full_name":resource_name
    }
    #res = {"package_id":"package_name", "name":resource_name, "created_in_gcs":"true", "gcs_full_name":resource_name}
    response = requests.post("http://localhost/api/3/action/resource_create", headers=auth, data=res)
    created_resource = response.json().get("result")
    res_id = created_resource.get("id")
    res_url = get_resource_url(created_resource)

    assert res_url == f"https://storage.cloud.google.com/wrc_wro_test/agriculture/structured/refined/time series/130-211-222-159-metadata-form-heeet-maize-northern-cape-2012/data for manuscript/cloud_logo_id_{res_id}.png"

def test_get_package_name(resource, auth):
    """
    packages names are unique 
    """
    name = resource.get("name")
    package_name = main.get_package_name(name, auth)
    assert package_name == "130-211-222-159-metadata-form-heeet-maize-northern-cape-2012"

    #full_url = 'https://storage.cloud.google.com/'+container_name+'/'+resource_cloud_path+'/'+ pkg_name + "/" + full_name


def test_resource_short_name(resource) -> dict:
    name = resource.get("name")
    short_name = main.get_resource_short_name(name)
    assert short_name == "cloud_logo"

def test_get_resource_format(resource):
    name = resource.get("name")
    format = main.get_resource_format(name)
    assert format == "png"


def test_get_resource_underscored_url(ckan_resource, auth):
    response = requests.post("http://localhost/api/3/action/resource_create", headers=auth, data=ckan_resource)
    created_resource = response.json()
    created_resource = created_resource.get("result")
    resource_url = get_resource_url(created_resource)
    underscored_url = main.get_resource_underscored_url(resource_url)
    assert underscored_url.get("updated_url") == resource_url

def test_new_blob_name(ckan_resource, auth):
    response = requests.post("http://localhost/api/3/action/resource_create", headers=auth, data=ckan_resource)
    created_resource = response.json()
    created_resource = created_resource.get("result")
    resource_url = get_resource_url(created_resource)
    underscored_url = main.get_resource_underscored_url(resource_url).get("updated_url")
    blob_rename_text = main.get_resource_underscored_url(resource_url, "wrc_wro_test").get("new_blob_name")
    remove_domain = underscored_url.replace("https://storage.cloud.google.com/","")
    print(remove_domain)
    bucket_name, new_blob_name = remove_domain.split("/",1)
    assert new_blob_name == blob_rename_text

def get_resource_url(resource):
    resource_url = resource.get("url")
    first_path, resource_name = resource_url.rsplit("/",1)
    resource_name_stem, resource_ext = Path(resource_name).stem, Path(resource_name).suffix
    resource_name_stem = resource_name_stem.replace(" ","_")
    underscored_url = first_path + "/" + resource_name_stem + resource_ext
    
    return underscored_url