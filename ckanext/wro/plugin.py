import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import config
from . import helpers
from .logic import converters, validators
from .logic.action import create, update
from .blueprints.map import map_blueprint
from .blueprints.xml_parser import xml_parser_blueprint
from .blueprints.download import download_blueprint
from .cli import commands


class WroPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)

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
        Return an empty dict for now.
        This prevents CKAN from failing when no custom actions exist.
        """
        return {
            'resource_create': create.resource_create
        }

    def get_commands(self):
        return [
            commands.wro
        ]

    # IBlueprint
    def get_blueprint(self):
        return [map_blueprint, xml_parser_blueprint, download_blueprint]

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
        }

    # IPackageController
    def before_index(self, pkg_dict):
        """
        Convert authors field from list of dicts to list of strings for Solr indexing.
        authors may be at the top level (list of dicts from scheming) or in extras
        (JSON string). Both are handled here, and the extras entry is always removed
        so CKAN's extras processor cannot overwrite the converted value.
        """
        import json

        # Resolve authors from top-level or extras
        authors = pkg_dict.get('authors')
        if authors is None:
            for extra in pkg_dict.get('extras', []):
                if extra.get('key') == 'authors':
                    authors = extra.get('value')
                    break

        # Always strip authors from extras to prevent CKAN overwriting below
        pkg_dict['extras'] = [
            e for e in pkg_dict.get('extras', [])
            if e.get('key') != 'authors'
        ]

        if authors is not None:
            # Parse JSON string if needed
            if isinstance(authors, str):
                try:
                    authors = json.loads(authors)
                except (json.JSONDecodeError, ValueError):
                    authors = None

            if not isinstance(authors, list):
                pkg_dict.pop('authors', None)
            else:
                author_strings = []
                for author in authors:
                    if isinstance(author, dict):
                        name_parts = []
                        if author.get('author_name'):
                            name_parts.append(str(author['author_name']))
                        if author.get('author_surname'):
                            name_parts.append(str(author['author_surname']))
                        author_str = ' '.join(name_parts)
                        if author.get('author_organization'):
                            author_str += f" ({author['author_organization']})"
                        if author_str:
                            author_strings.append(author_str)
                    elif isinstance(author, str):
                        author_strings.append(author)

                pkg_dict['authors'] = author_strings

        return pkg_dict

    # IPackageController
    def after_show(self, context, pkg_dict):
        """
        Flatten data_reference_date for search indexing only.

        data_reference_date (scheming simple_subfields) is stored as an extra
        whose value is a JSON string encoding a single-item list containing a
        {from, to} dict, e.g. '[{"data_reference_date_from": "...", ...}]'.
        ckan's core indexer (ckan/lib/search/index.py) copies extras onto the
        top-level dict verbatim (it only flattens list/tuple values, and a
        JSON string isn't one), then - because the key ends in "_date" -
        tries to dateutil.parse() that raw JSON string, fails, logs an ERROR
        and drops the field. Replace the extra here with flat from/to extras
        instead, whose keys don't end in "_date" so they index untouched.

        Both synchronous (on save) and `search-index rebuild` indexing call
        package_show with validate=False, which view/edit/API callers never
        set - used here to only touch the indexing copy of pkg_dict and leave
        the nested structure the edit form relies on untouched everywhere else.
        """
        if context.get('validate') is not False:
            return pkg_dict

        import json

        extras = pkg_dict.get('extras', [])
        date_extra = next(
            (e for e in extras if e.get('key') == 'data_reference_date'), None
        )
        if date_extra is None:
            return pkg_dict

        date_ref = date_extra.get('value')
        if isinstance(date_ref, str):
            try:
                date_ref = json.loads(date_ref)
            except (json.JSONDecodeError, ValueError):
                date_ref = None
        if isinstance(date_ref, list) and date_ref:
            date_ref = date_ref[0]

        new_extras = [e for e in extras if e.get('key') != 'data_reference_date']
        if isinstance(date_ref, dict):
            if date_ref.get('data_reference_date_from'):
                new_extras.append({
                    'key': 'data_reference_date_from',
                    'value': date_ref['data_reference_date_from'],
                })
            if date_ref.get('data_reference_date_to'):
                new_extras.append({
                    'key': 'data_reference_date_to',
                    'value': date_ref['data_reference_date_to'],
                })
        pkg_dict['extras'] = new_extras

        return pkg_dict

    # IResourceController
    def before_show(self, resource_dict):
        if 'download_count' not in resource_dict:
            resource_dict['download_count'] = '0'
        return resource_dict

    # IPackageController
    def before_dataset_create(self, context, data_dict):
        """Copy author data to contact person if checkbox is checked."""
        return converters.copy_author_to_contact(data_dict)

    def before_dataset_update(self, context, current, data_dict):
        """Copy author data to contact person if checkbox is checked."""
        return converters.copy_author_to_contact(data_dict)

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