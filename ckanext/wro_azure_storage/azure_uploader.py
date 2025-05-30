import os.path
import pathlib

import ckan
from ckan.common import config
import ckan.plugins.toolkit as toolkit
from ckan import model
from ckan.lib import munge
import ckan.plugins as p

from .azure_functions import upload_blob
from .azure_functions import delete_blob
from werkzeug.datastructures import FileStorage as FlaskFileStorage
from tempfile import SpooledTemporaryFile
import cgi
from ckan.common import config
import logging
log = logging.getLogger(__name__)  # Place this at the top of your file
_get_or_bust = ckan.logic.get_or_bust

ALLOWED_UPLOAD_TYPES = (cgi.FieldStorage, FlaskFileStorage)


def _get_underlying_file(wrapper):
    if isinstance(wrapper, FlaskFileStorage):
        return wrapper.stream
    return wrapper.file

class ResourceCloudStorage():
    def __init__(self, resource):
        """
        Support for uploading resources to any storage provider
        implemented by the apache-libcloud library.
        :param resource: The resource dict.
        """

        self.filename = None
        self.old_filename = None
        self.file = None
        self.resource = resource
        upload_field_storage = resource.pop('upload', None)
        self._clear = resource.pop('clear_upload', None)
        # ===========================
        # checking if the resource is provided as a link or is it a bigquery table
        is_resource_link = self.resource.get('is_link')
        if is_resource_link is None or is_resource_link is False:
            self.is_resource_link = False
        else:
            self.is_resource_link = True
        is_resource_bigquery_table = self.resource.get("is_bigquery_table")
        if is_resource_bigquery_table is None or is_resource_bigquery_table is False:
            self.is_bigquery_table = False
        else:
            self.is_bigquery_table = True
        # ===========================
        # Check to see if a file has been provided
        if isinstance(upload_field_storage, (ALLOWED_UPLOAD_TYPES)):
            self.filename = munge.munge_filename(upload_field_storage.filename)
            self.file_upload = _get_underlying_file(upload_field_storage)
            resource['url_type'] = 'upload'
        elif self._clear and resource.get('id'):
            # Apparently, this is a created-but-not-commited resource whose
            # file upload has been canceled
            old_resource = model.Session.query(model.Resource).get(resource['id'])
            self.old_filename = old_resource.url
            resource['url_type'] = ''

    def path_from_filename(self, rid, filename):
        """
        Returns a bucket path for the given resource_id and filename.
        :param rid: The resource ID.
        :param filename: The unmunged resource filename.
        """
        # you can get "wro theme" here, agriculture, water, ..etc.
        # and construct dynamic urls inisde the container
        
        # get the wro_theme
        res = toolkit.get_action('resource_show')(data_dict={'id':rid})
        package = toolkit.get_action('package_show')(data_dict={'id':res.get("package_id")})
        # we need to generate unique names inside the container
        name = pathlib.Path(filename).stem
        ext = pathlib.Path(filename).suffix
        name = self.change_file_name_to_bucket_compatible(name)
        file_name = name +'_id_'+ rid + ext
        package_extras = package.get("extras")
        cloud_path = ""
        if package_extras is not None:
            for item in package_extras:
                if item.get("key") == "cloud_path":
                    cloud_path = item.get("value")
        package_name = package.get("name")
        return os.path.join(
            cloud_path,
            package_name,
            file_name
        )

    def upload(self, id, max_size=10):
        """
        Complete the file upload, or clear an existing upload.
        :param id: The resource_id.
        :param max_size: Ignored.
        """
        if self.is_resource_link is False and self.is_bigquery_table is False:
            if self.filename:
                if isinstance(self.file_upload, SpooledTemporaryFile):
                    self.file_upload.next = self.file_upload._file
                    # try except here is a guard when
                    # the user remove the file and provide
                    # nothing
                    try:
                        upload_path = self.path_from_filename(id,self.filename)
                        log.debug(f"upload_path: {upload_path}")
                        account_name = config.get('azure_account_name')
                        storage_path = f'https://{account_name}.blob.core.windows.net/{upload_path}'
                        self.resource.update({'url' : storage_path})
                        bucket_name = config.get('bucket_name')
                        package = toolkit.get_action('package_show')(data_dict={'id':self.resource.get("package_id")})
                        package_id = package.get("id")
                        store_in_bigquery = self.resource.get("file_to_bigquery_table")
                        upload_blob(bucket_name, self.file_upload, upload_path, package_id, store_in_bigquery)
                    except Exception as e:
                        # Customize this message as needed
                        raise RuntimeError(f"Failed to upload to Azure Blob Storage: {e}")

        elif self.is_bigquery_table is True:
            # handle bigqyery tables, set the name of the resource
            self.resource["name"] = self.resource["resource_name"]

        # this is when the user change the file to a url via "remove" button
        elif self._clear and self.old_filename:  # and not self.leave_files
            # This is only set when a previously-uploaded file is replaced
            # by a link. We want to delete the previously-uploaded file.
            try:
               delete_blob(self.old_filename)
            except:
                # It's possible for the object to have already been deleted, or
                # for it to not yet exist in a committed state due to an
                # outstanding lease.
                return

    @property
    def package(self):
        return model.Package.get(self.resource['package_id'])

    def change_file_name_to_bucket_compatible(self, name):
        """
        google cloud bucket
        changes every special
        character (including spaces)
        into underscore, this results
        in the resource not being found
        """
        name = str(name).replace(" ", "_")
        for i in name:
            if i in "!”#$%&'()*+,-:;<=>?@[\]^`{|}~":
                name = name.replace(i,"_")
        return name