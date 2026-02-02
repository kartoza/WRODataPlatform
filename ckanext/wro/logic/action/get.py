"""Get actions for download tracking."""
import ckan.plugins.toolkit as toolkit
from ckanext.wro.model.download_stats import DownloadStats


@toolkit.side_effect_free
def resource_download_count(context, data_dict):
    """Get the download count for a resource.

    :param resource_id: the id of the resource
    :type resource_id: string

    :returns: download count
    :rtype: int
    """
    toolkit.check_access('resource_download_count', context, data_dict)

    resource_id = toolkit.get_or_bust(data_dict, 'resource_id')

    return {
        'count': DownloadStats.get_resource_download_count(resource_id)
    }


@toolkit.side_effect_free
def package_download_count(context, data_dict):
    """Get the download count for all resources in a package.

    :param package_id: the id or name of the package
    :type package_id: string

    :returns: download count
    :rtype: int
    """
    toolkit.check_access('package_download_count', context, data_dict)

    package_id = toolkit.get_or_bust(data_dict, 'package_id')

    # Get package to validate it exists
    package = toolkit.get_action('package_show')(context, {'id': package_id})

    return {
        'count': DownloadStats.get_package_download_count(package['id'])
    }
