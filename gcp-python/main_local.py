from google.cloud import storage
from google.cloud import bigquery
import zipfile
import logging
import io
import geopandas
import json
import os
import csv

import requests
from requests import get, post


class Default:
    PROJECT_ID = 'thermal-glazing-350010'
    BUCKET_NAME = 'wro-trigger-test'
    BUCKET_PROCESSED = 'wro-done'
    BUCKET_TEMP = 'wro-temp'
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

    NASA_POWER_URL = 'https://power.larc.nasa.gov/api/temporal'
    NASA_POWER_FORMAT = 'CSV'
    NASA_POWER_COMMUNITY = 'RE'  # AG, RE, or SB
    NASA_POWER_TEMPORAL_AVE = ['daily', 'monthly', 'climatology']

    SA_GRID_EXTENTS = [
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "16.057872772",  # left
            "lon_max": "19.057872772"  # right
        },
        {
            "lat_min": "-33.623123168999996",  # bottom
            "lat_max": "-30.623123169",  # top
            "lon_min": "16.057872772",  # left
            "lon_max": "19.057872772"  # right
        },
        {
            "lat_min": "-36.623123168999996",  # bottom
            "lat_max": "-33.623123168999996",  # top
            "lon_min": "16.057872772",  # left
            "lon_max": "19.057872772"  # right
        },
        {
            "lat_min": "-27.623123169",  # bottom
            "lat_max": "-24.623123169",  # top
            "lon_min": "19.057872772",  # left
            "lon_max": "22.057872772"  # right
        },
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "19.057872772",  # left
            "lon_max": "22.057872772"  # right
        },
        {
            "lat_min": "-33.623123168999996",  # bottom
            "lat_max": "-30.623123169",  # top
            "lon_min": "19.057872772",  # left
            "lon_max": "22.057872772"  # right
        },
        {
            "lat_min": "-36.623123168999996",  # bottom
            "lat_max": "-33.623123168999996",  # top
            "lon_min": "19.057872772",  # left
            "lon_max": "22.057872772"  # right
        },
        {
            "lat_min": "-27.623123169",  # bottom
            "lat_max": "-24.623123169",  # top
            "lon_min": "22.057872772",  # left
            "lon_max": "25.057872772"  # right
        },
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "22.057872772",  # left
            "lon_max": "25.057872772"  # right
        },
        {
            "lat_min": "-33.623123168999996",  # bottom
            "lat_max": "-30.623123169",  # top
            "lon_min": "22.057872772",  # left
            "lon_max": "25.057872772"  # right
        },
        {
            "lat_min": "-36.623123168999996",  # bottom
            "lat_max": "-33.623123168999996",  # top
            "lon_min": "22.057872772",  # left
            "lon_max": "25.057872772"  # right
        },
        {
            "lat_min": "-24.623123169",  # bottom
            "lat_max": "-21.623123169",  # top
            "lon_min": "25.057872772",  # left
            "lon_max": "28.057872772"  # right
        },
        {
            "lat_min": "-27.623123169",  # bottom
            "lat_max": "-24.623123169",  # top
            "lon_min": "25.057872772",  # left
            "lon_max": "28.057872772"  # right
        },
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "25.057872772",  # left
            "lon_max": "28.057872772"  # right
        },
        {
            "lat_min": "-33.623123168999996",  # bottom
            "lat_max": "-30.623123169",  # top
            "lon_min": "25.057872772",  # left
            "lon_max": "28.057872772"  # right
        },
        {
            "lat_min": "-36.623123168999996",  # bottom
            "lat_max": "-33.623123168999996",  # top
            "lon_min": "25.057872772",  # left
            "lon_max": "28.057872772"  # right
        },
        {
            "lat_min": "-24.623123169",  # bottom
            "lat_max": "-21.623123169",  # top
            "lon_min": "28.057872772",  # left
            "lon_max": "31.057872772"  # right
        },
        {
            "lat_min": "-27.623123169",  # bottom
            "lat_max": "-24.623123169",  # top
            "lon_min": "28.057872772",  # left
            "lon_max": "31.057872772"  # right
        },
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "28.057872772",  # left
            "lon_max": "31.057872772"  # right
        },
        {
            "lat_min": "-33.623123168999996",  # bottom
            "lat_max": "-30.623123169",  # top
            "lon_min": "28.057872772",  # left
            "lon_max": "31.057872772"  # right
        },
        {
            "lat_min": "-24.623123169",  # bottom
            "lat_max": "-21.623123169",  # top
            "lon_min": "31.057872772",  # left
            "lon_max": "34.057872771999996"  # right
        },
        {
            "lat_min": "-27.623123169",  # bottom
            "lat_max": "-24.623123169",  # top
            "lon_min": "31.057872772",  # left
            "lon_max": "34.057872771999996"  # right
        },
        {
            "lat_min": "-30.623123169",  # bottom
            "lat_max": "-27.623123169",  # top
            "lon_min": "31.057872772",  # left
            "lon_max": "34.057872771999996"  # right
        }
    ]


class Definitions:
    TEMP = {
        'key': 'T2M',
        'name': 'Temperature',
        'description': 'Temperature at 2 meters'
    }
    DEW_FROST = {
        'key': 'T2MDEW',
        'name': 'Frost',
        'description': 'Dew/frost point at 2 meters'
    }
    WET_TEMP = {
        'key': 'T2MWET',
        'name': 'Wet_temperature',
        'description': 'Wet bulb temperature at 2 meters'
    }
    EARTH_SKIN_TEMP = {
        'key': 'TS',
        'name': 'Earth_skin_temperature',
        'description': 'Earth skin temperature'
    }
    TEMP_RANGE = {
        'key': 'T2M_RANGE',
        'name': 'Temperature_range',
        'description': 'Temperature at 2 meters range'
    }
    TEMP_MAX = {
        'key': 'T2M_MAX',
        'name': 'Temperature_max',
        'description': 'Temperature at 2 meters maximum'
    }
    TEMP_MIN = {
        'key': 'T2M_MIN',
        'name': 'Temperature_min',
        'description': 'Temperature at 2 meters minimum'
    }
    SPECIFIC_HUMIDITY = {
        'key': 'QV2M',
        'name': 'Specific_humidity',
        'description': 'Specific humidity at 2 meters'
    }
    RELATIVE_HUMIDITY = {
        'key': 'RH2M',
        'name': 'Relative_humidity',
        'description': 'Relative humidity at meters'
    }
    PRECIPITATION = {
        'key': 'PRECTOTCORR',
        'name': 'Precipitation',
        'description': 'Precipitation'
    }
    SURFACE_PRESSURE = {
        'key': 'PS',
        'name': 'Surface_pressure',
        'description': 'Surface pressure'
    }
    WINDSPEED_10M = {
        'key': 'WS10M',
        'name': 'Windspeed_10m',
        'description': 'Wind speed at 10 meters'
    }
    WINDSPEED_10M_MAX = {
        'key': 'WS10M_MAX',
        'name': 'Windspeed_max_10m',
        'description': 'Wind speed at 10 meters maximum'
    }
    WINDSPEED_10M_MIN = {
        'key': 'WS10M_MIN',
        'name': 'Windspeed_min_10m',
        'description': 'Wind speed at 10 meters minimum'
    }
    WINDSPEED_10M_RANGE = {
        'key': 'WS10M_RANGE',
        'name': 'Windspeed_range_10m',
        'description': 'Wind speed at 10 meters range'
    }
    WIND_DIRECTION_10M = {
        'key': 'WD10M',
        'name': 'Wind_direction_10m',
        'description': 'Wind direction at 10 meters'
    }
    WINDSPEED_50M = {
        'key': 'WS50M',
        'name': 'Windspeed_50m',
        'description': 'Wind speed at 50 meters'
    }
    WINDSPEED_50M_MAX = {
        'key': 'WS50M_MAX',
        'name': 'Windspeed_max_50m',
        'description': 'Wind speed at 50 meters maximum'
    }
    WINDSPEED_50M_MIN = {
        'key': 'WS50M_MIN',
        'name': 'Windspeed_min_50m',
        'description': 'Wind speed at 50 meters minimum'
    }
    WINDSPEED_50M_RANGE = {
        'key': 'WS50M_RANGE',
        'name': 'Windspeed_range_50m',
        'description': 'Wind speed at 50 meters range'
    }
    WIND_DIRECTION_50M = {
        'key': 'WD50M',
        'name': 'Wind_direction_50m',
        'description': 'Wind direction at 50 meters'
    }

    LIST_NASA_POWER_DATASETS = [
        TEMP,
        DEW_FROST,
        WET_TEMP,
        EARTH_SKIN_TEMP,
        TEMP_RANGE,
        TEMP_MAX,
        TEMP_MIN,
        SPECIFIC_HUMIDITY,
        RELATIVE_HUMIDITY,
        PRECIPITATION,
        SURFACE_PRESSURE,
        WINDSPEED_10M,
        WINDSPEED_10M_MAX,
        WINDSPEED_10M_MIN,
        WINDSPEED_10M_RANGE,
        WIND_DIRECTION_10M,
        WINDSPEED_50M,
        WINDSPEED_50M_MAX,
        WINDSPEED_50M_MIN,
        WINDSPEED_50M_RANGE,
        WIND_DIRECTION_50M,
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
        list_vector = []

        for blob in bucket.list_blobs():
            content_name = blob.name
            if content_name.endswith('.csv'):
                list_csv.append(content_name)
            elif content_name.endswith('.zip') or content_name.endswith('.7z'):
                list_archives.append(content_name)
            elif content_name.endswith('.shp'):
                list_vector.append(content_name)

        return list_csv, list_excel, list_archives, list_raster, list_vector

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

        # Returns if the file has been moved
        return True

    @staticmethod
    def load_csv_into_bigquery(upload_uri, bq_table_uri, schema, skip_leading_rows=1):
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
        try:
            table = bigquery.Table(bq_table_uri, schema=schema)
            table = client_bq.create_table(table)
        except Exception as e:
            print("Could not create BigQuery table " + bq_table_uri)
            print("EXCEPTION: " + str(e))
            return False

        try:
            job_config = bigquery.LoadJobConfig(
                schema=schema,
                skip_leading_rows=skip_leading_rows,
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

        # Returns True if loading the data into BigQuery succeeded
        return True

    @staticmethod
    def convert_json_to_newline_json(data_json):
        """Convert JSON/GEOJSON to newline JSON. This is required for BigQuery table creation.

        :param data_json: JSON/GEOJSON data
        :type data_json: JSON/GEOJSON

        :returns: Newline JSON formatted string
        :rtype: Newline JSON
        """
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

        print('shp found')

        gc_shp = 'gs://' + Default.BUCKET_NAME + '/' + shp_file

        shp_geopandas = geopandas.read_file(gc_shp)
        shp_json = json.loads(shp_geopandas.to_json())
        newline_json = Utilities.convert_json_to_newline_json(shp_json)

        print('newline json created')

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

        print('start load')

        load_job = client_bq.load_table_from_json(newline_json, bq_table_uri, job_config=job_config)
        load_job.result()

        print('done')

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

            if zipfile.is_zipfile(zipbytes):
                with zipfile.ZipFile(zipbytes, 'r') as myzip:
                    for contentfilename in myzip.namelist():
                        contentfile = myzip.read(contentfilename)

                        blob_upload = bucket.blob(contentfilename)
                        blob_upload.upload_from_string(contentfile)
        except Exception as e:
            # Loading from csv file into bigquery failed
            # The newly created bigquery table will be deleted
            print("Could unzip " + zip_file)
            print("EXCEPTION: " + str(e))
            return False

        # Returns True if the file unzipped correctly
        return True


def data_added_to_bucket():
    """Trigger function to call when data has been uploaded to a bucket.
    Deploy this function to a Google cloud storage bucket
    """
    # BigQuery client
    client_bq = bigquery.Client()
    client = storage.Client(project=Default.PROJECT_ID)
    bucket = client.get_bucket(Default.BUCKET_NAME)

    list_csv, list_excel, list_archives, list_raster, list_vector = Utilities.list_bucket_data(
        project=Default.PROJECT_ID,
        bucket=Default.BUCKET_NAME)

    for csv_file in list_csv:
        output_table_name = csv_file.replace('.csv', '')
        upload_uri = 'gs://' + Default.BUCKET_NAME + '/' + csv_file
        bq_table_uri = Default.PROJECT_ID + '.' + Default.BIQGUERY_DATASET + '.' + output_table_name

        success = Utilities.load_csv_into_bigquery(upload_uri, bq_table_uri, Default.SCHEMA, 1)
        if success:
            moved = Utilities.move_data(Default.BUCKET_NAME, Default.BUCKET_PROCESSED, csv_file, csv_file)

    for archive_file in list_archives:
        success = Utilities.unzip(archive_file)
        if success:
            bucket.delete_blob(archive_file)

    for shp_file in list_vector:
        Utilities.shp_to_geojson(shp_file)


def download_weather_data():
    """Downloads data from NASA POWER
    """
    skip_leading_rows = 10  # Number of rows which will be skipped at the start of the file
    skip_trailing_rows = 1  # Number of rows at the enc of the file which will be skipped

    for period in Default.NASA_POWER_TEMPORAL_AVE:
        if period == 'daily':
            # YYYYMMDD for 'daily'
            date_required = True
            start_date = '20210101'
            end_date = '20210131'
        elif period == 'monthly':
            # YYYY for 'monthly'
            date_required = True
            start_date = '2021'
            end_date = '2022'
        else:
            # Date not required for 'climatology'
            date_required = False
            start_date = ''  # YYYYMMDD
            end_date = ''  # YYYYMMDD

        for dataset in Definitions.LIST_NASA_POWER_DATASETS:
            dataset_key = dataset['key']
            dataset_name = dataset['name']
            dataset_description = dataset['description']

            table_name = '{}_{}_{}_{}'.format(
                dataset_name,
                period,
                start_date,
                end_date
            )

            file_name = table_name + '.csv'
            file_dir = 'nasa_test/' + file_name
            with io.StringIO() as file_mem:
                for extent in Default.SA_GRID_EXTENTS:
                    lat_min = extent["lat_min"]
                    lat_max = extent["lat_max"]
                    lon_min = extent["lon_min"]
                    lon_max = extent["lon_max"]

                    if date_required:
                        link = '{}/{}/regional?parameters={}&start={}&end={}&community={}&format={}&latitude-min={}&latitude-max={}&longitude-min={}&longitude-max={}'.format(
                            Default.NASA_POWER_URL,
                            period,
                            dataset_key,
                            start_date,
                            end_date,
                            Default.NASA_POWER_COMMUNITY,
                            Default.NASA_POWER_FORMAT,
                            lat_min,
                            lat_max,
                            lon_min,
                            lon_max
                        )
                    else:
                        link = '{}/{}/regional?parameters={}&community={}&format={}&latitude-min={}&latitude-max={}&longitude-min={}&longitude-max={}'.format(
                            Default.NASA_POWER_URL,
                            period,
                            dataset_key,
                            Default.NASA_POWER_COMMUNITY,
                            Default.NASA_POWER_FORMAT,
                            lat_min,
                            lat_max,
                            lon_min,
                            lon_max
                        )

                    result = requests.get(link)
                    content = result.content

                    # Newline not stored as '\n' character, so use r'\n'
                    split_content = str(content).split(r'\n')

                    # Removes unwanted lines
                    split_content = split_content[skip_leading_rows:(len(split_content) - skip_trailing_rows)]

                    for line in split_content:
                        file_mem.write(line)
                        file_mem.write('\n')

                    # Utilities.write_to_file(file_dir, split_content)

                client = storage.Client(project=Default.PROJECT_ID)
                bucket = client.bucket(Default.BUCKET_TEMP)

                blob = bucket.blob(file_name)
                blob.upload_from_string(file_mem.getvalue())

                schema = [
                    bigquery.SchemaField('LAT', 'FLOAT', mode='NULLABLE'),
                    bigquery.SchemaField('LON', 'FLOAT', mode='NULLABLE'),
                    bigquery.SchemaField('YEAR', 'INTEGER', mode='NULLABLE'),
                    bigquery.SchemaField('MONTH', 'INTEGER', mode='NULLABLE'),
                    bigquery.SchemaField('DAY', 'INTEGER', mode='NULLABLE'),
                    bigquery.SchemaField(table_name, 'FLOAT', mode='NULLABLE')
                ]

                upload_uri = 'gs://' + Default.BUCKET_TEMP + '/' + file_name
                bq_table_uri = Default.PROJECT_ID + '.' + Default.BIQGUERY_DATASET + '.' + table_name

                Utilities.load_csv_into_bigquery(upload_uri, bq_table_uri, schema, skip_leading_rows=0)

                bucket.delete_blob(file_name)

            # remove
            return


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    # data_added_to_bucket()
    download_weather_data()