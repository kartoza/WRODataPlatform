from google.cloud import bigquery


def get_bigquery_datasets():
    """A list of the datasets stored in a project BigQuery

    :returns: List of tables found in the provided dataset
    :rtype: list
    """

    client = bigquery.Client()

    datasets = list(client.list_datasets())

    dataset_names = []
    for dataset in datasets:
        dataset_names.append(dataset.dataset_id)

    return dataset_names


def get_tables():
    """A list of the tables stored in a project BigQuery. The list includes the dataset name as well.

    :returns: List of tables found in the provided dataset
    :rtype: list
    """

    client = bigquery.Client()

    list_dataset_names = get_bigquery_datasets()

    list_tables = []
    for dataset_name in list_dataset_names:
        dataset_tables = client.list_tables(dataset_name)

        for table in dataset_tables:
            table_name = table.table_id
            list_tables.append({
                'dataset': dataset_name,
                'table': table_name
            })
    return list_tables


list_bq_data = get_tables()

print(str(list_bq_data))
