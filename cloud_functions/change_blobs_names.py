import pathlib
from google.cloud import storage

def initialize_google_storage_client():
    service_account_path = "/home/mohab/Main/development/googleAuthKeys/wro project/wrc-wro-0fb140f089db.json"
    storage_client = storage.Client.from_service_account_json(service_account_path)
    return storage_client

def list_cloud_resources():
    """
    change the names of 
    few resources.
    """
    client = initialize_google_storage_client()
    bucket = client.bucket("wrc_wro_datasets")
    for res in bucket.list_blobs(prefix="agriculture/structured/access/both/sapwat3/sapwat3"):
        name = change_name(res)
        if name is not None:
            new_name = "agriculture/structured/access/both/sapwat3/SAPWAT3/TABLES/WEATHERDATA/" + name
            bucket.rename_blob(res, new_name)
            #print(name)

def change_name(blob):
    res_name = blob.name
    path, id = res_name.split("_id_")
    ext = pathlib.Path(id).suffix
    path, name = path.rsplit("/",1)
    if not "/tables/" in path:
        pass
    else:
        full_name = name.upper() + ext
        return full_name

list_cloud_resources()