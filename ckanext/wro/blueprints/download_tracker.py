"""Blueprint for tracking and redirecting resource downloads."""
from flask import Blueprint, redirect, request, send_file
import ckan.plugins.toolkit as toolkit
from ckan import model
import ckan.lib.uploader as uploader
import logging
import os

log = logging.getLogger(__name__)

download_tracker_blueprint = Blueprint('download_tracker', __name__)


@download_tracker_blueprint.route('/dataset/<package_id>/resource/<resource_id>/download/<filename>')
def track_and_download(package_id, resource_id, filename):
    """Track the download and redirect to the actual resource URL."""

    # Get the resource
    try:
        resource = toolkit.get_action('resource_show')(
            {'ignore_auth': True},
            {'id': resource_id}
        )
    except toolkit.ObjectNotFound:
        toolkit.abort(404, 'Resource not found')

    # Log the download
    context = {
        'user': toolkit.g.user if hasattr(toolkit.g, 'user') else None,
        'model': model,
        'ignore_auth': True
    }

    try:
        toolkit.get_action('log_resource_download')(
            context,
            {'resource_id': resource_id}
        )
        log.info(f"Logged download for resource {resource_id}")
    except Exception as e:
        log.error(f"Failed to log download: {e}")

    # Get the actual download URL
    # For uploaded files, serve directly from storage
    if resource.get('url_type') == 'upload':
        try:
            # Get the uploader and file path
            upload = uploader.get_resource_uploader(resource)
            filepath = upload.get_path(resource['id'])

            # Serve the file directly
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            log.error(f"Failed to serve file: {e}")
            toolkit.abort(404, 'File not found')
    else:
        # For external URLs, redirect directly
        return redirect(resource['url'])


@download_tracker_blueprint.route('/dataset/<package_id>/resource/<resource_id>/track-download')
def track_download_ajax(package_id, resource_id):
    """AJAX endpoint to track downloads without redirect."""

    context = {
        'user': toolkit.g.user if hasattr(toolkit.g, 'user') else None,
        'model': model,
        'ignore_auth': True
    }

    try:
        result = toolkit.get_action('log_resource_download')(
            context,
            {'resource_id': resource_id}
        )
        return {'success': True, 'download_logged': result}
    except Exception as e:
        log.error(f"Failed to log download: {e}")
        return {'success': False, 'error': str(e)}, 500
