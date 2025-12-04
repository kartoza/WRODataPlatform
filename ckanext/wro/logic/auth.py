"""Authorization functions for download tracking."""
import ckan.plugins.toolkit as toolkit


def log_resource_download(context, data_dict):
    """Anyone can log a download (even anonymous users)."""
    return {'success': True}


def resource_download_count(context, data_dict):
    """Anyone can view download counts."""
    return {'success': True}


def package_download_count(context, data_dict):
    """Anyone can view download counts."""
    return {'success': True}
