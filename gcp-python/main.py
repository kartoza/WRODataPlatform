import io
import zipfile
import geopandas
import json

from google.cloud import storage
from google.cloud import bigquery


class Default:
    PROJECT_ID = 'thermal-glazing-350010'
    BUCKET_NAME = 'wro-trigger-test'
    BUCKET_PROCESSED = 'wro-done'
    BIQGUERY_DATASET = 'hydro_test'

    SCHEMA = [
        # bigquery.SchemaField('Date', 'Date', mode='NULLABLE'),
        bigquery.SchemaField('Max_Temperature', 'FLOAT', mode='NULLABLE'),
        bigquery.SchemaField('Min_Temperature', 'FLOAT', mode='NULLABLE'),
        bigquery.SchemaField('Precipitation', 'FLOAT', mode='NULLABLE'),
        bigquery.SchemaField('Relative_Humidity', 'FLOAT', mode='NULLABLE'),
        bigquery.SchemaField('Solar', 'FLOAT', mode='NULLABLE'),
        bigquery.SchemaField('Streamflow', 'FLOAT', mode='NULLABLE'),
    ]


class Utilities:
    @staticmethod
    def list_bucket_data(project, bucket):
        """Lists files contained in a bucket.

        :param project: Google cloud platform project ID
        :type project: String

        :param bucket: Google cloud platform bucket name
        :type bucket: String

        :returns: Lists containing files directories.
        :rtype: List
        """
        # Storage client
        client = storage.Client(project=project)
        buckets = client.list_buckets()
        bucket = client.get_bucket(bucket)

        list_csv = []
        list_excel = []
        list_archives = []
        list_raster = []

        for blob in bucket.list_blobs():
            content_name = blob.name
            if content_name.endswith('.csv'):
                list_csv.append(content_name)
            elif content_name.endswith('.zip') or content_name.endswith('.7z'):
                list_archives.append(content_name)

        return list_csv, list_excel, list_archives, list_raster

    @staticmethod
    def move_data(source_bucket, destination_bucket, source_file, destination_file):
        """Moves a file from a bucket to other location or bucket.

        :param source_bucket: Bucket name where the file is stored
        :type source_bucket: String

        :param destination_bucket: Destination bucket name to which the file will be moved
        :type destination_bucket: String

        :param source_file: File which will be moved
        :type source_file: String

        :param destination_file: Location to which the file will be moved
        :type destination_file: String

        :returns: True if data move has been successful, false if data move has failed
        :rtype: boolean
        """
        try:
            client = storage.Client(project=Default.PROJECT_ID)
            bucket = client.bucket(source_bucket)
            destination_bucket = client.bucket(destination_bucket)

            blob_to_move = bucket.blob(source_file)
            blob_copy = bucket.copy_blob(
                blob_to_move,
                destination_bucket,
                destination_file
            )
        except Exception as e:
            # Loading from csv file into bigquery failed
            # The newly created bigquery table will be deleted
            print("Could not move " + source_file)
            print("EXCEPTION: " + str(e))
            return False

        # Deletes the source file if the file has been copied to the destination
        bucket.delete_blob(source_file)

        # Returns True if the file has been moved
        return True

    @staticmethod
    def load_csv_into_bigquery(upload_uri, bq_table_uri):
        """Loads a CSV file stored in a bucket into BigQuery.

        :param upload_uri: Google cloud storage directory (e.g. gs://bucket/folder/file)
        :type upload_uri: String

        :param bq_table_uri: Google cloud storage directory (e.g. gs://bucket/folder/file)
        :type bq_table_uri: String

        :param schema: Fields structure of the BigQuery table
        :type schema: List

        :param skip_leading_rows: Number of rows to skip at the start of the file
        :type skip_leading_rows: Integer

        :returns: True if the CSV data has been stored in BigQuery successful, false if it failed
        :rtype: boolean
        """
        client_bq = bigquery.Client()
        client = storage.Client(project=Default.PROJECT_ID)

        try:
            table = bigquery.Table(bq_table_uri, schema=Default.SCHEMA)
            table = client_bq.create_table(table)
        except Exception as e:
            print("Could not create BigQuery table " + bq_table_uri)
            print("EXCEPTION: " + str(e))
            return False

        try:
            job_config = bigquery.LoadJobConfig(
                schema=Default.SCHEMA,
                skip_leading_rows=1,
                source_format=bigquery.SourceFormat.CSV
            )

            load_job = client_bq.load_table_from_uri(
                upload_uri, bq_table_uri, job_config=job_config
            )
            load_job.result()
        except Exception as e:
            # Loading from csv file into bigquery failed
            # The newly created bigquery table will be deleted
            print("Could not load " + upload_uri)
            print("EXCEPTION: " + str(e))
            client_bq.delete_table(bq_table_uri)
            return False

        return True

    @staticmethod
    def convert_json_to_newline_json(data_json):
        """Convert JSON/GEOJSON to newline JSON. This is required for BigQuery table creation.

        :param data_json: JSON/GEOJSON data
        :type data_json: JSON/GEOJSON

        :returns: Newline JSON formatted string
        :rtype: Newline JSON
        """
        print('json to newline')

        list_newline_json = []

        list_features = data_json['features']
        for feature in list_features:
            feat_properties = feature['properties']
            feat_id = feat_properties['id']
            feat_desc = feat_properties['desc']
            feat_geom = feature['geometry']

            new_json_feat = {
                'id': feat_id,
                'desc': feat_desc,
                'geometry': feat_geom
            }
            list_newline_json.append(new_json_feat)

        return list_newline_json

    @staticmethod
    def shp_to_geojson(shp_file):
        """Converts a shapefile stored in Google cloud storage GEOJSON.

        :param shp_file: Google cloud storage directory of the shapefile (e.g. gs://bucket/folder/file.shp)
        :type shp_file: Shapefile
        """

        gc_shp = 'gs://' + Default.BUCKET_NAME + '/' + shp_file

        print('shp: ' + str(gc_shp))

        shp_geopandas = geopandas.read_file(gc_shp)
        #shp_geopandas = gp.read_file(gc_shp)

        print("AFTER shp")

        print(str(shp_geopandas))

        shp_json = json.loads(shp_geopandas.to_json())
        newline_json = Utilities.convert_json_to_newline_json(shp_json)

        print('data read')

        client_bq = bigquery.Client()

        bq_table_uri = Default.PROJECT_ID + '.' + Default.BIQGUERY_DATASET + '.' + shp_file.replace('.shp', '')

        schema = [
            bigquery.SchemaField('id', 'INTEGER', mode='NULLABLE'),
            bigquery.SchemaField('desc', 'STRING', mode='NULLABLE'),
            bigquery.SchemaField('geometry', 'GEOGRAPHY', mode='NULLABLE'),
        ]

        table = bigquery.Table(bq_table_uri, schema=schema)
        table = client_bq.create_table(table)

        print('table created')

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )

        print('load')

        load_job = client_bq.load_table_from_json(newline_json, bq_table_uri, job_config=job_config)
        load_job.result()

    @staticmethod
    def write_to_file(file, lines):
        """Writes lines to a text/CSV file.

        :param file: Output/target file
        :type file: String

        :param lines: Variable which contains a list of the lines which needs to be written to the file
        :type lines: List
        """
        if not os.path.exists(file):
            # File does not exist, create it
            with open(file, 'w') as f:
                for line in lines:
                    f.write(line)
                    f.write('\n')
        else:
            # File exists, append to it
            with open(file, 'a') as f:
                for line in lines:
                    f.write(line)
                    f.write('\n')
        f.close()

    @staticmethod
    def unzip(zip_file):
        """Unzips a zip file stored in a Google cloud storage bucket.

        :param zip_file: Google cloud storage directory (e.g. gs://bucket/folder/file.zip)
        :type zip_file: String

        :returns: True if the zip file extracted successfully, false if it failed
        :rtype: boolean
        """
        try:
            client = storage.Client(project=Default.PROJECT_ID)
            bucket = client.get_bucket(Default.BUCKET_NAME)

            blob = bucket.blob(zip_file)
            zipbytes = io.BytesIO(blob.download_as_string())

            # Checks if the file is a zip file
            if zipfile.is_zipfile(zipbytes):
                # Opens the zip file
                with zipfile.ZipFile(zipbytes, 'r') as myzip:
                    for contentfilename in myzip.namelist():
                        contentfile = myzip.read(contentfilename)

                        # Uploads the file in the zip file to the bucket
                        blob_upload = bucket.blob(contentfilename)
                        blob_upload.upload_from_string(contentfile)
        except Exception as e:
            # Unpacking the zip file failed
            print("Could not unzip " + zip_file)
            print("EXCEPTION: " + str(e))
            return False

        # Returns True if the file unzipped correctly
        return True


# [START functions_bucket_storage]
def data_added_to_bucket(event, context):
    """Trigger function to call when data has been uploaded to a bucket.
    Deploy this function to a Google cloud storage bucket
    """
    # Google platform
    client_bq = bigquery.Client()
    client = storage.Client(project=Default.PROJECT_ID)
    bucket = client.get_bucket(Default.BUCKET_NAME)

    # Trigger variables
    bucket_name = event['bucket']
    uploaded_file = event['name']
    event_id = context.event_id
    event_type = context.event_type
    metageneration = event['metageneration']
    time_created = event['timeCreated']
    updated = event['updated']

    if uploaded_file.endswith('.csv'):
        output_table_name = uploaded_file.replace('.csv', '')
        upload_uri = 'gs://' + bucket_name + '/' + uploaded_file
        bq_table_uri = Default.PROJECT_ID + '.' + Default.BIQGUERY_DATASET + '.' + output_table_name

        success = Utilities.load_csv_into_bigquery(upload_uri, bq_table_uri)
        if success:
            moved = Utilities.move_data(Default.BUCKET_NAME, Default.BUCKET_PROCESSED, uploaded_file, uploaded_file)
    elif uploaded_file.endswith('.zip'):
        success = Utilities.unzip(uploaded_file)
        if success:
            bucket.delete_blob(uploaded_file)
    elif uploaded_file.endswith('.shp'):
        Utilities.shp_to_geojson(uploaded_file)
# [END functions_bucket_storage]
