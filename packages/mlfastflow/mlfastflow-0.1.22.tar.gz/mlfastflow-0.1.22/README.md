# MLFastFlow

A Python package for fast dataflow and workflow processing.

## Installation

```bash
pip install mlfastflow
```

## Features

- Easy-to-use data sourcing with the Sourcing class
- Flexible vector search capabilities
- Optimized for data processing workflows

## Quick Start

```python
from mlfastflow import Sourcing

# Create a sourcing instance
sourcing = Sourcing(
    query_df=your_query_dataframe,
    db_df=your_database_dataframe,
    columns_for_sourcing=["column1", "column2"],
    label="your_label"
)

# Process your data
sourced_db_df_without_label, sourced_db_df_with_label = (
    sourcing.sourcing()
)
```

## BigQuery Integration

MLFastFlow provides a powerful `BigQueryClient` class for seamless integration with Google BigQuery and Google Cloud Storage (GCS).

### Initialization

```python
from mlfastflow import BigQueryClient

# Initialize the client with your GCP credentials
bq_client = BigQueryClient(
    project_id="your-gcp-project-id",
    dataset_id="your_dataset",
    key_file="/path/to/your/service-account-key.json"
)
```

### Running SQL Queries

```python
# Execute a SQL query and get results as a pandas DataFrame
df = bq_client.sql2df("SELECT * FROM your_dataset.your_table LIMIT 10")

# Or simply run a query without returning results
bq_client.run_sql("CREATE TABLE your_dataset.new_table AS SELECT * FROM your_dataset.source_table")
```

### DataFrame to BigQuery

```python
import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie'],
    'value': [100, 200, 300]
})

# Upload DataFrame to BigQuery
bq_client.df2table(
    df=df,
    table_id="your_table_name",
    if_exists="fail"  # Options: 'fail',  'append'
)
```

### BigQuery to Google Cloud Storage

```python
# Export query results to GCS as Parquet files (default)
bq_client.sql2gcs(
    sql="SELECT * FROM your_dataset.your_table",
    destination_uri="gs://your-bucket/path/to/export/",
    destination_format="PARQUET"  # Options: 'PARQUET', 'CSV', 'JSON', 'AVRO'
)

```

### Google Cloud Storage to BigQuery

```python
# Load data from GCS to BigQuery
bq_client.gcs2table(
    gcs_uri="gs://your-bucket/path/to/data/*.parquet",
    table_id="your_destination_table",
    write_disposition="WRITE_TRUNCATE",  # Options: 'WRITE_TRUNCATE', 'WRITE_APPEND', 'WRITE_EMPTY'
    source_format="PARQUET"  # Options: 'PARQUET', 'CSV', 'JSON', 'AVRO', 'ORC'
)
```

### GCS Folder Management

```python
# Create a folder in GCS
bq_client.create_gcs_folder("gs://your-bucket/new-folder/")

# Delete a folder and all its contents
success, deleted_count = bq_client.delete_gcs_folder(
    gcs_folder_path="gs://your-bucket/folder-to-delete/",
    dry_run=True  # Set to False to actually delete
)
print(f"Would delete {deleted_count} files" if success else "Error occurred")
```

### Resource Management

```python
# Explicitly close the client when done to free resources
bq_client.close()
del bq_client
bq_client = None
```



For more detailed examples and advanced usage, refer to the [documentation](https://github.com/Xileven/mlfastflow/docs).

## License

MIT

## Author

Xileven
