from feast import FileSource

properties_parquet_file = "../data_sources/features.parquet"

properties_source = FileSource(
    name="properties_source",
    path=properties_parquet_file,
    timestamp_field="date_posted"
)

