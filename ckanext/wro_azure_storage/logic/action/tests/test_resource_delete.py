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
    assert created_resource.get("name") == "resource_name"
    response = requests.post("http://localhost/api/3/action/resource_delete", headers=auth, data={"id":resource_id})
    response = requests.get(f"http://localhost/api/3/action/resource_show?id={resource_id}", headers=auth)
    print(response.status_code)
    assert response.status_code == 404

def test_resource_deleted_from_gcs():
    pass
