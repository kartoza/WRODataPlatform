import ckan.plugins as p

# allowd types by flask 
import cgi
from werkzeug.datastructures import FileStorage as FlaskFileStorage
ALLOWED_UPLOAD_TYPES = (cgi.FieldStorage, FlaskFileStorage)

class GCSUploader:
    def __init__(self,data_dict) -> None:
        if data_dict:
            self.upload = data_dict['upload']
            self.file_name = data_dict['name']
            self.file_url = data_dict['url']
        if isinstance(self.upload, (ALLOWED_UPLOAD_TYPES)):
            pass