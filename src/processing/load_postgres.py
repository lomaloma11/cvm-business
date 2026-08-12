import logging
import os 
import pandas as pd
import sqlalchemy as sa
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_db_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")

    engine = sa.create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
    return engine

def populate_dim_date(engine):
    dates = pd.date_range(start="2024-01-01", end="2024-12-31")
    df_date = pd.DataFrame({"full_date": dates})
    df_date["date_id"] = df_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    df_date["day"] = df_date["full_date"].dt.day
    df_date["month"] = df_date["full_date"].dt.month
    df_date["month_name"] = df_date["full_date"].dt.strftime("%B")
    df_date["quarter"] = df_date["full_date"].dt.quarter
    df_date["year"] = df_date["full_date"].dt.year
    
    df_date.to_sql("dim_date", engine, if_exists="append", index=False)

def load_data_to_postgres():
    processed_dir = "data/processed/cvm"
    cad_parquet = os.path.join(processed_dir, "cad_fi_processed.parquet")
    inf_parquet = os.path.join(processed_dir, "inf_diario_processed.parquet")

    engine = get_db_engine()

    if os.path.exists(cad_parquet):
        df_cad = pd.read_parquet(cad_parquet)
        df_cad.columns = df_cad.columns.str.lower()
        df_cad["valid_from"] = pd.to_datetime("2024-01-01")
        df_cad["valid_to"] = None
        df_cad["is_current"] = True
        df_cad.to_sql("dim_fund", engine, if_exists="append", index=False)

    populate_dim_date(engine)

    if os.path.exists(inf_parquet):
        df_inf = pd.read_parquet(inf_parquet)
        df_inf.columns = df_inf.columns.str.lower()
        df_inf.to_sql("fact_informe_diario", engine, if_exists="append", index=False)

    logging.info("Carga no PostgreSQL concluída com sucesso!")

if __name__ == "__main__":
    load_data_to_postgres()


