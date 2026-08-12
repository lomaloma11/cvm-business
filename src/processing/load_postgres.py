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

def populate_dim_date(engine, start="2024-01-01", end="2024-12-31"):
    """Gera e popula a dimensão calendário apenas se ela estiver vazia."""
    logging.info("Verificando registros na tabela dim_date...")

    try:
        # Verifica a quantidade de linhas já existentes na dim_date
        count_df = pd.read_sql("SELECT COUNT(*) AS total FROM dim_date", engine)
        total_rows = count_df["total"].iloc[0]
        
        if total_rows > 0:
            logging.info(f"A tabela dim_date já contém {total_rows} registros. Inserção pulada.")
            return
    except Exception as e:
        logging.warning(f"Não foi possível verificar a dim_date: {e}")

    logging.info("Gerando e inserindo calendário na tabela dim_date...")
    dates = pd.date_range(start=start, end=end)
    df_date = pd.DataFrame({"full_date": dates})
    df_date["date_id"] = df_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    df_date["day"] = df_date["full_date"].dt.day
    df_date["month"] = df_date["full_date"].dt.month
    df_date["month_name"] = df_date["full_date"].dt.strftime("%B")
    df_date["quarter"] = df_date["full_date"].dt.quarter
    df_date["year"] = df_date["full_date"].dt.year
    
    df_date.to_sql("dim_date", engine, if_exists="append", index=False)

def load_data_to_postgres():
    bucket_name = os.getenv("S3_BUCKET_NAME", "cvm-business-datalake")
    
    s3_options = {
        "key": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "client_kwargs": {
            "region_name": os.getenv("AWS_REGION", "us-east-1")
        }
    }

    # Caminhos apontando diretamente para o S3
    cad_s3_path = f"s3://{bucket_name}/processed/cvm/cad_fi_processed.parquet"
    inf_s3_path = f"s3://{bucket_name}/processed/cvm/inf_diario_processed.parquet"

    try:
        engine = get_db_engine()

        # Carga da Dimensão Fundos a partir do S3
        logging.info(f"Lendo dim_fund diretamente do AWS S3 ({cad_s3_path})...")
        df_cad = pd.read_parquet(cad_s3_path, storage_options=s3_options)
        df_cad.columns = df_cad.columns.str.lower()
        
        existing_cnpjs = pd.read_sql("SELECT cnpj_fundo FROM dim_fund", engine)
        if not existing_cnpjs.empty:
            df_cad = df_cad[df_cad["cnpj_fundo"].isin(existing_cnpjs["cnpj_fundo"])]
            
        if not df_cad.empty:
            df_cad.to_sql("dim_fund", engine, if_exists="append", index=False)
            logging.info(f"dim_fund populada com {len(df_cad)} novos registros do S3.")
        else:
            logging.info("dim_fund já está atualizada com os registros do S3.")

        # Carga da Dimensão Calendário
        populate_dim_date(engine)

        # Carga da Tabela Fato a partir do S3
        logging.info(f"Lendo fact_informe_diario diretamente do AWS S3 ({inf_s3_path})...")
        df_inf = pd.read_parquet(inf_s3_path, storage_options=s3_options)
        df_inf.columns = df_inf.columns.str.lower()

        df_cad_cnpjs = pd.read_sql("SELECT cnpj_fundo FROM dim_fund", engine)
        df_inf = df_inf[df_inf["cnpj_fundo"].isin(df_cad_cnpjs["cnpj_fundo"])]

        df_inf.to_sql("fact_informe_diario", engine, if_exists="append", index=False)
        logging.info(f"fact_informe_diario populada com {len(df_inf)} registros do S3.")

        logging.info("Carga via AWS S3 concluída com sucesso no PostgreSQL!")

    except Exception as e:
        logging.critical(f"Erro durante a carga via AWS S3: {e}")

if __name__ == "__main__":
    load_data_to_postgres()


