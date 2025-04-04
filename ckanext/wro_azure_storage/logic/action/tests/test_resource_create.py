import pytest
import requests
# i want to test the url of the resource, is it correct

@pytest.fixture
def resource():
    """
    a fixture can
    be passed as an
    argument
    """
    return {
        "package_id":"130-211-222-159-metadata-form-heeet-maize-northern-cape-2012",
        "name":"resource_name.csv",
        "format":"csv",
        "url":"",
        "resource_type":""
    }

# cloud_path = Agriculture/Structured/Access/Time Series/Package id/

@pytest.fixture
def auth():
    return {"Authorization":"6d5f1cf7-6d42-467f-b27f-b0a8454572c0"}

def test_resource_create(resource, auth):
    response = requests.post("http://localhost/api/3/action/resource_create", headers=auth, data=resource)
    created_resource = response.json().get("result")
    res_url = get_resource_url(created_resource)
    res_url = res_url.lower()
    assert created_resource.get("url") == res_url
    # cleanup
    id = created_resource.get("id")
    response = requests.post("http://localhost/api/3/action/resource_delete", headers=auth, data={"id":id})

def get_resource_url(resource):
    resource_id = resource.get("id")
    resource_name = resource.get("name")
    resource_name, resource_ext = resource_name.split(".")
    format = resource.get("format")
    full_name = resource_name+"_id_"+resource_id+"."+format
    pkg_name = "130-211-222-159-metadata-form-heeet-maize-northern-cape-2012"
    resource_url = f"https://storage.cloud.google.com/wrc_wro_test/agriculture/structured/refined/time series/{pkg_name}/{full_name}"
    return resource_url