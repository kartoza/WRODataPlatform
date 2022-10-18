import pandas as pd
from datetime import datetime


# remove this it was just for testing

def excel_into_bq(excel_file):
        """Stores an Excel file in Google storage in BigQuery

        :param excel_file: Google cloud storage directory of the Excel file (e.g. gs://bucket/folder/file.xlxs)
        :type excel_file: xlsx
        """
        now = datetime.now()
        print('[' + str(now) + '] ' + "Reading the Excel file using pandas")

        # client_bq = bigquery.Client()
        service_account_path = "/home/mohab/Main/development/googleAuthKeys/wro project/wrc-wro-0fb140f089db.json"
        pd_excel_file = pd.read_excel(excel_file, storage_options={"token":service_account_path})
        print(pd_excel_file)
        # excel_sheet_names = pd_excel_file.sheet_names
        # num_of_sheets = len(excel_sheet_names)

        # # Loops through the sheets.
        # for sheet_name in excel_sheet_names:
        #     now = datetime.now()
        #     print('[' + str(now) + '] ' + "Sheet: " + sheet_name)

            # # Removes unwanted characters from sheet names
            # parsed_sheet_name = Utilities.parse_column_names([sheet_name])
            # parsed_sheet_name = parsed_sheet_name[0]

            # # Table name
            # if num_of_sheets > 1:
            #     # If there is more than one sheet, the sheet name will be used to distinguish tables names for BQ
            #     if excel_file.endswith('.xlsx'):
            #         table_name = os.path.basename(excel_file).replace('.xlsx', '_' + parsed_sheet_name)
            #     else:
            #         table_name = os.path.basename(excel_file).replace('.xls', '_' + parsed_sheet_name)
            # else:
            #     # Sheet name will not be used for the table name as there are only one sheet
            #     if excel_file.endswith('.xlsx'):
            #         table_name = os.path.basename(excel_file).replace('.xlsx', '')
            #     else:
            #         table_name = os.path.basename(excel_file).replace('.xls', '')
            # bq_table_uri = Default.PROJECT_ID + '.' + Default.BIGQUERY_DATASET_BUCKET + '.' + table_name

            # # Quick test to see of the BigQuery table exists
            # try:
            #     table_bq = client_bq.get_table(bq_table_uri)
            #     table_exist = True
            # except NotFound:
            #     table_exist = False
            # if table_exist:
            #     # Table exists, skip
            #     now = datetime.now()
            #     print('[' + str(now) + '] ' + "Table exists: " + table_name)
            #     continue

            # try:
            #     pandas_excel = pd.read_excel(excel_file, sheet_name)
            #     list_data_types = pandas_excel.dtypes

            #     schema = []
            #     column_names_orig = list(pandas_excel.columns.values)

            #     column_names_parsed = Utilities.parse_column_names(column_names_orig)  # Removes unwanted characters

            #     i = 0
            #     for field_name in column_names_orig:
            #         field_type = list_data_types[field_name]
            #         if pd.api.types.is_integer_dtype(field_type):
            #             f_type = 'INTEGER'
            #         elif pd.api.types.is_float_dtype(field_type):
            #             f_type = 'FLOAT'
            #         else:
            #             f_type = 'STRING'

            #         field_name_parsed = column_names_parsed[i]
            #         # Renames the field in the pandas dataframe
            #         pandas_excel.rename(columns={field_name: field_name_parsed}, inplace=True)

            #         schema.append(bigquery.SchemaField(
            #             field_name_parsed,
            #             f_type,
            #             mode='NULLABLE'
            #         ))

            #         i = i + 1

            #     table = bigquery.Table(bq_table_uri, schema=schema)
            #     client_bq.create_table(table)

            #     job_config = bigquery.LoadJobConfig(
            #         write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
            #     )

            #     load_job = client_bq.load_table_from_dataframe(pandas_excel, bq_table_uri, job_config=job_config)
            #     load_job.result()
            # except Exception as e:
            #     try:
            #         table_bq = client_bq.get_table(bq_table_uri)
            #     except NotFound:
            #         # Deletes the table if it has been created
            #         client_bq.delete_table(bq_table_uri)
            #     print("Excel table/sheet could not be imported into BigQuery.")
            #     print(str(e))
            #     continue

path = "gs://wrc_wro_datasets/agriculture/structured/refined/time series/maize-long-term-trial/long_term_trial_datasets_id_6603b69c-53f2-43f7-9574-97c67206ec56.xlsx"
excel_into_bq(path)