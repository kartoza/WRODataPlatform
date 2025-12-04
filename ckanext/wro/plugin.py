import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import config
from . import helpers
from .logic import converters, validators, auth
from .logic.action import create, update, get
from .blueprints.map import map_blueprint
from .blueprints.xml_parser import xml_parser_blueprint
from .blueprints.download_tracker import download_tracker_blueprint
from .cli import commands


class WroPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IPackageController, inherit=True)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic',
            'wro')
        toolkit.add_resource('assets','wro_assets')

    def get_validators(self) -> dict:
        return {
            "convert_raw_input_to_geojson": converters.convert_raw_input_to_geojson,
            "conditional_date_reference_validator": validators.conditional_date_reference_validator,
            "author_same_as_contact": validators.author_same_as_contact,
            "agreement": validators.agreement,
            "author_or_contact_collected_data": validators.author_or_contact_collected_data,
            "lower_case":validators.lower_case, 
            "empty_resource_info":converters.convert_empty_resource_info_to_false,
        }

    def get_actions(self):
        """
        Return custom actions for the WRO extension.
        """
        return {
            'resource_create': create.resource_create,
            'log_resource_download': create.log_resource_download,
            'resource_download_count': get.resource_download_count,
            'package_download_count': get.package_download_count,
        }

    def get_auth_functions(self):
        """
        Return authorization functions for the WRO extension.
        """
        return {
            'log_resource_download': auth.log_resource_download,
            'resource_download_count': auth.resource_download_count,
            'package_download_count': auth.package_download_count,
        }

    def get_commands(self):
        return [
            commands.wro
        ]

    # IBlueprint
    def get_blueprint(self):
        return [map_blueprint, xml_parser_blueprint, download_tracker_blueprint]

    # helpers
    def get_helpers(self):
        return {
            "get_bigquery_table_name": helpers.get_bigquery_table_name,
            "get_package_name":helpers.get_package_name,
            "convert_geojson_to_bbox":helpers.convert_geojson_to_bbox,
            "get_default_bounding_box":helpers.get_default_bounding_box,
            'resource_read_helper':helpers.resource_read_helper,
            "get_package_count": helpers.get_packages_count,
            "get_org_count":helpers.get_organizations_count,
            "get_default_spatial_search_extent":helpers.get_default_spatial_search_extent,
            "get_resource_download_count": helpers.get_resource_download_count,
            "get_package_download_count": helpers.get_package_download_count,
        }

    # IPackageController
    def before_dataset_index(self, pkg_dict):
        """
        Convert authors field from list of dicts to list of strings for Solr indexing
        """
        import json
        import logging

        log = logging.getLogger(__name__)

        if 'authors' in pkg_dict:
            authors = pkg_dict['authors']

            # Log original value for debugging
            log.debug(f"Original authors value: {authors} (type: {type(authors)})")

            # If authors is a string (JSON), parse it first
            if isinstance(authors, str):
                try:
                    authors = json.loads(authors)
                except (json.JSONDecodeError, ValueError):
                    # If it fails, just remove it from indexing
                    log.warning(f"Failed to parse authors JSON: {authors}")
                    del pkg_dict['authors']
                    return pkg_dict

            # If authors is a list, convert to list of strings
            if isinstance(authors, list) and authors:
                author_strings = []
                for author in authors:
                    # Handle both dict and already-string cases
                    if isinstance(author, dict):
                        # Build author string from available fields
                        name_parts = []
                        if author.get('author_name'):
                            name_parts.append(str(author['author_name']))
                        if author.get('author_surname'):
                            name_parts.append(str(author['author_surname']))

                        author_str = ' '.join(name_parts) if name_parts else ''

                        # Add organization if available
                        if author.get('author_organization'):
                            author_str += f" ({author['author_organization']})"

                        if author_str:
                            author_strings.append(author_str)
                    elif isinstance(author, str):
                        # Already a string, just use it
                        author_strings.append(author)

                pkg_dict['authors'] = author_strings
                log.debug(f"Converted authors to: {author_strings}")
            elif not isinstance(authors, list):
                # If it's not a list, remove it from indexing
                log.warning(f"Authors is not a list, removing from index: {type(authors)}")
                del pkg_dict['authors']

        return pkg_dict


    # IResourceView

    def info(self):
        """
        setup the view configuration
        """
        return {
            'name': 'bigquery_map_view',
            'title': toolkit._('Bigquery Map View'),
            'icon': 'map-marker',
            'always_available': True,
            'iframed': False,
            }

    
    def setup_template_variables(self, context, data_dict):
        pass

    def view_template(self, context, data_dict):
        """
        setup the view template
        """
        return 'views/bigquery_map_view.html'

class TabularFileView(WroPlugin):

    def get_helpers(self):
        return {
            "parse_cloud_tabular_data": helpers.parse_cloud_tabular_data,
        }

    #IResource
    def info(self):
        return {'name': 'tabular_view',
            'title': 'Tabular Explorer',
            'filterable': True,
            'icon': 'table',
            'requires_datastore': False,
            'always_available': True,
            'default_title': toolkit._('Tabular Explorer'),
            }

    def can_view(self, data_dict):
        resource = data_dict.get("resource")
        if resource is None:
            return False
        if resource.get('format'):
            return resource.get("format").lower() == "csv"
    

    def setup_template_variables(self, context, data_dict):
        pass

    def view_template(self, context, data_dict):
        """
        setup the view template
        """
        return 'views/tabular_view.html'


class CustomImageView(WroPlugin):
    # plugins.implements(plugins.IResourceView, inherit=True)
    # plugins.implements(plugins.IConfigurer, inherit=True)

    # adding assets
    # def update_config(self, config_):
    #     toolkit.add_template_directory(config_, 'templates')
    #     toolkit.add_public_directory(config_, 'public')
    #     toolkit.add_resource('fanstatic','wro')
    #     toolkit.add_resource('assets','wro_assets')
        
    #IResource
    def info(self):
        return {'name': 'custom_image_view',
            'title': 'Image',
            'filterable': True,
            'icon': 'image',
            'requires_datastore': False,
            'always_available': True,
            'default_title': toolkit._('Image'),
            }

    def can_view(self, data_dict):
        resource = data_dict.get("resource")
        if resource is None:
            return False
        if resource.get('format'):
            return resource.get("format").lower() in ["png", "jpeg", "jpg"]
    

    def setup_template_variables(self, context, data_dict):
        pass

    def view_template(self, context, data_dict):
        """
        setup the view template
        """
        return 'views/custom_image_view.html'