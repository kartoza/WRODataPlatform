import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

def get_groups():
    groups = toolkit.get_action('group_list')(data_dict={'sort':'package_count desc'})
    return groups


class TemplateChangerPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic',
            'template_changer')
        toolkit.add_resource('assets','template_changer_assets')

    def get_helpers(self):
        return {'get_groups':get_groups}