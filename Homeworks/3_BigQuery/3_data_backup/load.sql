COPY rides_dataset.rides FROM './3_data_backup/rides_dataset_rides.parquet' (FORMAT 'parquet');
COPY rides_dataset._dlt_loads FROM './3_data_backup/rides_dataset__dlt_loads.parquet' (FORMAT 'parquet');
COPY rides_dataset._dlt_pipeline_state FROM './3_data_backup/rides_dataset__dlt_pipeline_state.parquet' (FORMAT 'parquet');
COPY rides_dataset._dlt_version FROM './3_data_backup/rides_dataset__dlt_version.parquet' (FORMAT 'parquet');
