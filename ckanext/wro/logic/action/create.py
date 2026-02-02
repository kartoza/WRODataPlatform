import ckan.logic as logic
_get_action = logic.get_action
import ckan.plugins.toolkit as toolkit, plugins
from werkzeug.datastructures import FileStorage
import ckan.lib.uploader as uploader
import tempfile
import logging
import shutil
import zipfile
import os
import mimetypes
from ckanext.wro.model.download_stats import DownloadStats


logger = logging.getLogger(__name__)


def log_resource_download(context, data_dict):
    """Log a resource download event.

    :param resource_id: the id of the resource
    :type resource_id: string

    :returns: download log entry
    :rtype: dict
    """
    resource_id = toolkit.get_or_bust(data_dict, 'resource_id')

    # Get resource to validate it exists and get package_id
    resource = toolkit.get_action('resource_show')(context, {'id': resource_id})
    package_id = resource['package_id']

    # Get user info from context
    user_id = context.get('user')
    if user_id:
        try:
            user_obj = context.get('model').User.get(user_id)
            user_id = user_obj.id if user_obj else None
        except:
            user_id = None

    # Get IP address and user agent from request
    from flask import request
    ip_address = request.remote_addr if request else None
    user_agent = request.user_agent.string if request and hasattr(request, 'user_agent') else None

    # Log the download
    download = DownloadStats.log_download(
        resource_id=resource_id,
        package_id=package_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return {
        'id': download.id,
        'resource_id': download.resource_id,
        'package_id': download.package_id,
        'downloaded_at': download.downloaded_at.isoformat()
    }


@toolkit.chained_action
def package_create(original_action, context, data_dict):
    logger.warning(context)
    logger.warning(data_dict)
    return
    data_dict["type"] = "metadata-form"
    access = toolkit.check_access("package_create", context, data_dict)
    result = original_action(context, data_dict) if access else None
    return result


@toolkit.chained_action
def resource_create(original_action, context: dict, data_dict: dict) -> dict:
    model = context['model']
    user = context['user']
    logger.warning(context)
    logger.warning(data_dict)

    package_id = toolkit.get_or_bust(data_dict, 'package_id')
    if not data_dict.get('url'):
        data_dict['url'] = ''

    toolkit.check_access('resource_create', context, data_dict)

    for plugin in plugins.PluginImplementations(plugins.IResourceController):
        plugin.before_create(context, data_dict)

    # detect zip
    is_zip = data_dict['format'] == 'zip'

    created_resources = []

    # ---- case 1: normal file
    if not is_zip:
        resource = original_action(context, data_dict)
        created_resources.append(resource)
        return resource

    # ---- case 2: zip file
    # first create the resource for the zip itself
    zip_resource = original_action(context, data_dict)
    created_resources.append(zip_resource)

    if data_dict.get('extras', {}).get('zipped_file', False):
        # now extract the zip to a tempdir
        tmpdir = tempfile.mkdtemp()
        try:
            upload = uploader.ResourceUpload(zip_resource)
            zip_path = upload.get_path(zip_resource['id'])
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(tmpdir)

            # walk through extracted files
            for root, _, files in os.walk(tmpdir):
                for fname in files:
                    extracted_file = os.path.join(root, fname)
                    relpath = os.path.relpath(extracted_file, tmpdir)  # preserve nested paths
    #
                    with open(extracted_file, "rb") as f:
                        filename = relpath
                        file_storage = FileStorage(
                            stream=f,
                            filename=filename,
                            content_type=mimetypes.guess_type(filename)[0] or "application/octet-stream"
                        )
                        format = os.path.splitext(filename)[-1].replace('.', '').lower() or "unknown"
                        res_dict = {
                            "package_id": package_id,
                            "name": filename,  # descriptive is better if you have it
                            "upload": file_storage,
                            "format": format,
                            "url": filename,
                            "mimetype": file_storage.content_type,
                            "extras": {
                                "is_data_supplementary": "False",
                                "resource_name": filename,
                                "zipped_file": "True" if format == "zip" else False
                            }
                        }
                        try:
                            res = original_action(context, res_dict)
                            created_resources.append(res)
                        except Exception as e:
                            logger.error(f"Failed to create resource for {relpath}: {e}")
        finally:
            shutil.rmtree(tmpdir)

    return zip_resource
