from azure.storage.blob import BlobServiceClient, ContentSettings
import pathlib
from ckan.common import config
import os
from ckan.lib.helpers import flash_notice


def initialize_azure_client():
    connection_string = config.get('azure_connection_string')
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    return blob_service_client


def upload_blob(container_name, source_file, destination_blob_name, package_id, store_in_bigquery="false"):
    blob_service_client = initialize_azure_client()
    destination_blob_name = destination_blob_name.lower()

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=destination_blob_name)

    # Set content disposition for download
    content_disposition = get_content_disposition(destination_blob_name)

    # Read binary data from the file
    source_file.seek(0)
    file_data = source_file.read()

    content_settings = ContentSettings(
        content_type='application/octet-stream',
        content_disposition=content_disposition
    )

    metadata = {
        'package_id': package_id,
        'bigquery_file': "false" if store_in_bigquery is None else "true",
        'created_via_ckan': "true"
    }

    # Upload the blob
    blob_client.upload_blob(file_data, overwrite=True, content_settings=content_settings, metadata=metadata)


def delete_blob(package_name, resource_cloud_path, resource_dict):
    """
    Deletes a blob from Azure Blob Storage.
    """
    blob_service_client = initialize_azure_client()
    container_name = config.get('container_name')

    resource_name = resource_dict.get('name')
    if not resource_name:
        flash_notice("Could not delete resource from cloud, name is not provided")
        return

    resource_name = resource_name.replace(" ", "_")
    name = pathlib.Path(resource_name).stem
    ext = pathlib.Path(resource_name).suffix
    resource_id = resource_dict.get('id')
    if not resource_id:
        flash_notice("Could not delete resource from cloud, resource id is not provided")
        return

    resource_cloud_name = f"{resource_cloud_path}/{package_name}/{name}_id_{resource_id}{ext}".lower()
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=resource_cloud_name)

    try:
        blob_client.delete_blob()
    except Exception as e:
        flash_notice(f"Could not delete blob: {str(e)}")


def get_content_disposition(file_name):
    """
    Controls the download file name.
    """
    if "/" in file_name:
        remove_path = file_name[file_name.rfind("/") + 1:]
        ext = pathlib.Path(remove_path).suffix
        remove_id = remove_path[:remove_path.rfind("_id_")]
        new_name = remove_id + ext
        return f'attachment; filename="{new_name}"'
    return None
