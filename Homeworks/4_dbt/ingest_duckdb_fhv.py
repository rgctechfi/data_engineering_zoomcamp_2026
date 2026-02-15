from pathlib import Path

import duckdb
import requests

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
DATA_ROOT = BASE_DIR / "data" / "parquet" / "fhv"
DB_PATH = BASE_DIR / "data" / "database" / "taxi_rides_ny.duckdb"
BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv"
YEAR = 2019


def _sql_path(path: Path) -> str:
    return path.as_posix().replace("'", "''")


def update_gitignore() -> None:
    gitignore_path = PROJECT_ROOT / ".gitignore"
    content = gitignore_path.read_text() if gitignore_path.exists() else ""
    data_line = "Homeworks/4_dbt/data/parquet\n"

    if data_line not in content:
        with open(gitignore_path, "a", encoding="utf-8") as file:
            block = f"\n# Data directory\n{data_line}" if content else f"# Data directory\n{data_line}"
            file.write(block)


def download_and_convert_fhv_2019() -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()

    try:
        for month in range(1, 13):
            csv_gz_name = f"fhv_tripdata_{YEAR}-{month:02d}.csv.gz"
            parquet_name = f"fhv_tripdata_{YEAR}-{month:02d}.parquet"

            csv_gz_path = DATA_ROOT / csv_gz_name
            parquet_path = DATA_ROOT / parquet_name

            if parquet_path.exists():
                print(f"Skipping {parquet_name} (already exists)")
                continue

            url = f"{BASE_URL}/{csv_gz_name}"
            print(f"Downloading {csv_gz_name}...")
            response = requests.get(url, stream=True, timeout=120)
            response.raise_for_status()

            with open(csv_gz_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)

            print(f"Converting {csv_gz_name} to parquet...")
            con.execute(
                f"""
                COPY (
                    SELECT * FROM read_csv_auto('{_sql_path(csv_gz_path)}')
                )
                TO '{_sql_path(parquet_path)}' (FORMAT PARQUET)
                """
            )

            csv_gz_path.unlink(missing_ok=True)
            print(f"Completed {parquet_name}")
    finally:
        con.close()


def load_parquet_to_duckdb() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    parquet_glob = _sql_path(DATA_ROOT / f"fhv_tripdata_{YEAR}-*.parquet")

    con = duckdb.connect(DB_PATH.as_posix())
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS prod")
        con.execute(
            f"""
            CREATE OR REPLACE TABLE prod.fhv_tripdata AS
            SELECT *
            FROM read_parquet('{parquet_glob}', union_by_name=true)
            """
        )
    finally:
        con.close()


if __name__ == "__main__":
    update_gitignore()
    download_and_convert_fhv_2019()
    load_parquet_to_duckdb()
    print("FHV 2019 ingestion completed: prod.fhv_tripdata is ready.")
