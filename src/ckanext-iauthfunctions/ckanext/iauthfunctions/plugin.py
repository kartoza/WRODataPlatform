import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import config

def group_create(context, data_dict):
    user_name = context['user']
    is_ueser_allowed_to_create_groups = config.get
    ('ckanext.iauthfunctions.is_ueser_allowed_to_create_groups',False)
    allowance = toolkit.asbool(is_ueser_allowed_to_create_groups)
    if allowance:
        return {"sucess":True}
    else:
        return {"sucess":False, "msg":"you have to be loggin to create groups"}


class IauthfunctionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic',
            'iauthfunctions')
        toolkit.add_resource('asset','iauth_asset')

    def get_auth_functions(self):
        # you can override the authentication/authorization for different functions here
        return {'group_create':group_create}