import ckan.logic as logic
_get_action = logic.get_action
import ckan.plugins.toolkit as toolkit
import logging

logger = logging.getLogger(__name__)


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


# import os
# import zipfile
# import tempfile
# import shutil
# import pathlib
# from ckan.plugins import toolkit, plugins
# from ckan.lib import uploader
# import logging
#
# logger = logging.getLogger(__name__)
#
# @toolkit.chained_action
# def resource_create(original_action, context: dict, data_dict: dict) -> dict:
#     model = context['model']
#     user = context['user']
#
#     package_id = toolkit.get_or_bust(data_dict, 'package_id')
#     if not data_dict.get('url'):
#         data_dict['url'] = ''
#
#     pkg_dict = toolkit.get_action('package_show')(
#         dict(context, return_type='dict'),
#         {'id': package_id})
#
#     toolkit.check_access('resource_create', context, data_dict)
#
#     for plugin in plugins.PluginImplementations(plugins.IResourceController):
#         plugin.before_create(context, data_dict)
#
#     upload = uploader.get_resource_uploader(data_dict)
#
#     # detect zip
#     filename = data_dict.get("upload") or data_dict.get("url", "")
#     is_zip = filename.lower().endswith(".zip")
#
#     created_resources = []
#
#     # ---- case 1: normal file
#     if not is_zip:
#         resource = original_action(context, data_dict)
#         created_resources.append(resource)
#         return resource
#
#     # ---- case 2: zip file
#     # first create the resource for the zip itself
#     zip_resource = original_action(context, data_dict)
#     created_resources.append(zip_resource)
#
#     # now extract the zip to a tempdir
#     tmpdir = tempfile.mkdtemp()
#     try:
#         zip_path = upload.filepath
#         with zipfile.ZipFile(zip_path, "r") as zf:
#             zf.extractall(tmpdir)
#
#         # walk through extracted files
#         for root, _, files in os.walk(tmpdir):
#             for fname in files:
#                 extracted_file = os.path.join(root, fname)
#                 relpath = os.path.relpath(extracted_file, tmpdir)  # preserve nested paths
#
#                 res_dict = {
#                     "package_id": package_id,
#                     "name": relpath,  # keep folder structure
#                     "format": pathlib.Path(fname).suffix.replace(".", "").upper(),
#                 }
#
#                 with open(extracted_file, "rb") as f:
#                     res_dict["upload"] = f
#                     try:
#                         res = original_action(context, res_dict)
#                         created_resources.append(res)
#                     except Exception as e:
#                         logger.error(f"Failed to create resource for {relpath}: {e}")
#     finally:
#         shutil.rmtree(tmpdir)
#
#     return zip_resource