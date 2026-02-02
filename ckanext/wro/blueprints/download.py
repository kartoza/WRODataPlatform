"""Custom download blueprint to fix Content-Disposition filename issue.

CKAN 2.9.11 has a bug where the Content-Disposition header uses a truncated
resource UUID instead of the actual filename. This blueprint overrides the
default download route to fix this.
"""

import os
import mimetypes
from typing import Optional

from flask import Blueprint, send_file, Response
from ckan.plugins import toolkit
from ckan.lib import uploader
from ckan.common import config


download_blueprint = Blueprint(
    "wro_download",
    __name__,
    url_prefix="/dataset/<id>/resource/<resource_id>"
)


@download_blueprint.route("/download")
@download_blueprint.route("/download/<filename>")
def download(id: str, resource_id: str, filename: Optional[str] = None):
    """
    Custom download handler that properly sets Content-Disposition header.
    """
    context = {
        "user": toolkit.g.user,
        "auth_user_obj": toolkit.g.userobj
    }

    try:
        resource = toolkit.get_action("resource_show")(context, {"id": resource_id})
    except toolkit.ObjectNotFound:
        return toolkit.abort(404, toolkit._("Resource not found"))
    except toolkit.NotAuthorized:
        return toolkit.abort(403, toolkit._("Not authorized to read resource"))

    # Determine the filename to use
    if filename:
        # Use the filename from the URL path
        download_filename = filename
    elif resource.get("name"):
        # Fall back to resource name
        download_filename = resource["name"]
    elif resource.get("url"):
        # Extract filename from URL
        download_filename = resource["url"].split("/")[-1]
    else:
        # Last resort: use resource ID
        download_filename = resource_id

    # Check if this is an uploaded file
    if resource.get("url_type") == "upload":
        upload = uploader.get_resource_uploader(resource)
        filepath = upload.get_path(resource["id"])

        if not os.path.exists(filepath):
            return toolkit.abort(404, toolkit._("Resource file not found"))

        # Determine content type
        content_type = resource.get("mimetype")
        if not content_type:
            content_type, _ = mimetypes.guess_type(download_filename)
        if not content_type:
            content_type = "application/octet-stream"

        # Check if we should force attachment download
        force_attachment = toolkit.asbool(
            config.get("ckan.download.force_attachment", False)
        )

        # Build Content-Disposition header
        if force_attachment:
            disposition = f'attachment; filename="{download_filename}"'
        else:
            disposition = f'inline; filename="{download_filename}"'

        response = send_file(
            filepath,
            mimetype=content_type,
            as_attachment=force_attachment,
            download_name=download_filename
        )

        # Ensure the header is set correctly (override Flask's default)
        response.headers["Content-Disposition"] = disposition

        return response
    else:
        # External URL - redirect to it
        return toolkit.redirect_to(resource["url"])
