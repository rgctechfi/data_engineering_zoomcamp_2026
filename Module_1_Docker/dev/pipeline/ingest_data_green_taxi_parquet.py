#!/usr/bin/env python
# coding: utf-8

import pyarrow.parquet as pq
import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import requests
from io import BytesIO


@click.command()
#Postgres config
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port') #change port if necessary
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')

#Datas config
@click.option('--year', default=2025, type=int, help='Year of the data')
@click.option('--month', default=11, type=int, help='Month of the data')
@click.option('--target-table', default='green_taxi_data', help='Target table name')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for reading CSV')

def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table, chunksize, year, month):
    """Ingest NYC green taxi data into PostgreSQL database."""

    # 1. dynamic managing url (good practice)
    filename = f"green_tripdata_{year}-{month:02d}.parquet"
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{filename}"
    
    print(f"Connecting to Postgres...")
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    print(f"Downloading {url}...")
    
    # ASTUCE : Pour lire un Parquet distant en chunks, le mieux est de le charger 
    # dans un buffer ou de le télécharger localement d'abord.
    # Ici, on le charge en mémoire tampon pour le lire avec PyArrow.
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erreur lors du téléchargement: {response.status_code}")
        return

    # Ouvrir le fichier Parquet avec PyArrow
    parquet_file = pq.ParquetFile(BytesIO(response.content))
    
    print("Start ingesting data...")
    
    first = True
    
    # 2. La boucle magique : iter_batches
    for batch in tqdm(parquet_file.iter_batches(batch_size=chunksize), total=parquet_file.num_row_groups):
        
        # Convertir le batch PyArrow en DataFrame Pandas
        df_chunk = batch.to_pandas()

        if first:
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists='replace'
            )
            first = False

        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists='append'
        )

    print("Finished ingesting data.")

if __name__ == '__main__':
    run()