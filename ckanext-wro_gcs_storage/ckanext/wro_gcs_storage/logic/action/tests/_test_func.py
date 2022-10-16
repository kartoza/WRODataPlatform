import pytest
import requests
import ckanapi


@pytest.fixture
def resource():
    res = {
        "package_id":"130-211-222-159-metadata-form-heeet-maize-northern-cape-2012",
        "name":"resource_name",
        "format":"csv",
        "url":"",
        "resource_type":""
    }
    return res

@pytest.fixture
def auth():
    return {"Authorization":"3bcdec16-4d75-4804-8c8f-6830e3fc1dff"}

@pytest.fixture
def ckan():
    ckan = ckanapi.RemoteCKAN('http://localhost.com/', apikey='3bcdec16-4d75-4804-8c8f-6830e3fc1dff', user_agent='ckanapi so test')
    return ckan

def test_resource_deleted_from_ckan(resource, auth, ckan):
    response = requests.post("http://localhost/api/3/action/resource_create", headers=auth, data=resource)
    created_resource = response.json().get("result")
    resource_id = created_resource.get("id")
    created_resource = ckan.action.resource_show(**{"id":resource_id})
    assert created_resource.get("name") == "resource_name"
    response = requests.post("http://localhost/api/3/action/resource_delete", headers=auth, data={"id":resource_id})
    assert created_resource.get("name") == None

def test_resource_deleted_from_gcs():
    pass

# def get_res():
#     ckan = ckanapi.RemoteCKAN('http://localhost/', apikey='3bcdec16-4d75-4804-8c8f-6830e3fc1dff', user_agent='ckanapi so test')
#     # response = requests.get("http://localhost/api/3/action/resource_show", headers=auth, data={"id":"fd9999ab-9095-4494-bbba-a3f1779af10d"})
#     response = ckan.action.resource_show(**{"id":"fd9999ab-9095-4494-bbba-a3f1779af10d"})
#     print(response)

# get_res()
