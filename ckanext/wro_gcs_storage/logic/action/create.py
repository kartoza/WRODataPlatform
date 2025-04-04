# import os
# import ckan.logic as logic 
# import ckan.plugins as plugins
# import ckan.lib.uploader as uploader
# from ckan.common import config
# import pathlib
# import logging
# from socket import error as socket_error
# import ckan.common
# import ckan.logic as logic
# import ckan.plugins as plugins
# import ckan.lib.dictization
# import ckan.logic.action
# import ckan.logic.schema
# import ckan.lib.navl.dictization_functions
# import ckan.lib.uploader as uploader
# import ckan.lib.datapreview
# from ckan.common import _, config

# # FIXME this looks nasty and should be shared better
# from ckan.logic.action.update import _update_package_relationship

# log = logging.getLogger(__name__)

# # mohab, some customization
# from .actions_helpers import is_resource_link, is_resource_bigquery_table



# # Define some shortcuts
# # Ensure they are module-private so that they don't get loaded as available
# # actions in the action API.
# _validate = ckan.lib.navl.dictization_functions.validate
# _check_access = logic.check_access
# _get_action = logic.get_action
# ValidationError = logic.ValidationError
# NotFound = logic.NotFound
# NotAuthorized = logic.NotAuthorized
# _get_or_bust = logic.get_or_bust

# _check_access = logic.check_access
# _get_action = logic.get_action
# ValidationError = logic.ValidationError
# NotFound = logic.NotFound
# NotAuthorized = logic.NotAuthorized
# _get_or_bust = logic.get_or_bust

# def resource_create(context, data_dict):
#     '''Appends a new resource to a datasets list of resources.
#     :param package_id: id of package that the resource should be added to.
#     :type package_id: string
#     :param url: url of resource
#     :type url: string
#     :param description: (optional)
#     :type description: string
#     :param format: (optional)
#     :type format: string
#     :param hash: (optional)
#     :type hash: string
#     :param name: (optional)
#     :type name: string
#     :param resource_type: (optional)
#     :type resource_type: string
#     :param mimetype: (optional)
#     :type mimetype: string
#     :param mimetype_inner: (optional)
#     :type mimetype_inner: string
#     :param cache_url: (optional)
#     :type cache_url: string
#     :param size: (optional)
#     :type size: int
#     :param created: (optional)
#     :type created: iso date string
#     :param last_modified: (optional)
#     :type last_modified: iso date string
#     :param cache_last_updated: (optional)
#     :type cache_last_updated: iso date string
#     :param upload: (optional)
#     :type upload: FieldStorage (optional) needs multipart/form-data
#     :returns: the newly created resource
#     :rtype: dictionary
#     '''
#     model = context['model']
#     user = context['user']
#     package_id = _get_or_bust(data_dict, 'package_id')
#     if not data_dict.get('url'):
#         data_dict['url'] = ''
    
#     pkg_dict = _get_action('package_show')(
#         dict(context, return_type='dict'),
#         {'id': package_id})
#     _check_access('resource_create', context, data_dict)

#     for plugin in plugins.PluginImplementations(plugins.IResourceController):
#         plugin.before_create(context, data_dict)

#     if 'resources' not in pkg_dict:
#         pkg_dict['resources'] = []
#     data_dict = is_resource_link(data_dict)
#     data_dict= is_resource_bigquery_table(data_dict)
#     upload = uploader.get_resource_uploader(data_dict)

#     if 'mimetype' not in data_dict:
#         if hasattr(upload, 'mimetype'):
#             data_dict['mimetype'] = upload.mimetype

#     if 'size' not in data_dict:
#         if hasattr(upload, 'filesize'):
#             data_dict['size'] = upload.filesize

#     pkg_dict['resources'].append(data_dict)
#     try:
#         context['defer_commit'] = True
#         context['use_cache'] = False
#         _get_action('package_update')(context, pkg_dict)
#         context.pop('defer_commit')
#     except ValidationError as e:
#         try:
#             raise ValidationError(e.error_dict['resources'][-1])
#         except (KeyError, IndexError):
#             raise ValidationError(e.error_dict)

#     # Get out resource_id resource from model as it will not appear in
#     # package_show until after commit
#     upload.upload(context['package'].resources[-1].id,
#                   uploader.get_max_resource_size())
    
#     # mohab changed here
#     # need to change the resource before commiting to database name+rid+ext
#     the_res = context['package'].resources[-1]
#     the_cloud_path = the_res.extras['cloud_path']
#     resource_name = the_res.name    # this name is file name not the name of the resource provided in the form
#     name = pathlib.Path(resource_name).stem
#     ext = pathlib.Path(resource_name).suffix
#     full_name = name+'_id_'+context['package'].resources[-1].id+ext
#     container_name = config.get('container_name')
#     pkg_dict = _get_action('package_show')(context, {'id': package_id})
#     pkg_name = pkg_dict['name']
#     full_url = 'https://storage.cloud.google.com/'+container_name+'/'+the_cloud_path+'/'+ pkg_name + "/" +full_name
#     context['package'].resources[-1].url = f'{full_url}'
#     model.repo.commit()

#     #  Run package show again to get out actual last_resource
#     updated_pkg_dict = _get_action('package_show')(context, {'id': package_id})
#     resource = updated_pkg_dict['resources'][-1]
#     resource['url'] = full_url
#     # from here this the plugin
    
#     #  Add the default views to the new resource
#     logic.get_action('resource_create_default_resource_views')(
#         {'model': context['model'],
#          'user': context['user'],
#          'ignore_auth': True
#          },
#         {'resource': resource,
#          'package': updated_pkg_dict
#          })

#     for plugin in plugins.PluginImplementations(plugins.IResourceController):
#         plugin.after_create(context, resource)
#     return resource