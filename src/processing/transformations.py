import os
import sys
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from cleaning import clean_cadastro_fundos, clean_informe_diario
from validation import validate_dataframe

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_processing():
    raw_dir = "data/raw/cvm"
    processed_dir = "data/processed/cvm"
    os.makedirs(processed_dir, exist_ok=True)
    
    cad_path = os.path.join(raw_dir, "cad_fi.csv")
    inf_path = os.path.join(raw_dir, "inf_diario_fi_202401.csv")
    
    try:
        # Processamento do Cadastro
        if os.path.exists(cad_path):
            df_cad = clean_cadastro_fundos(cad_path)
            if validate_dataframe(df_cad, "Cadastro Fundos", "CNPJ_FUNDO"):
                output_cad = os.path.join(processed_dir, "cad_fi_processed.parquet")
                df_cad.to_parquet(output_cad, index=False)
                logging.info(f"Arquivo Parquet salvo em: {output_cad}")
        else:
            logging.warning(f"Arquivo {cad_path} não encontrado.")
            
        # Processamento do Informe Diário
        if os.path.exists(inf_path):
            df_inf = clean_informe_diario(inf_path)
            if validate_dataframe(df_inf, "Informe Diário", "CNPJ_FUNDO"):
                output_inf = os.path.join(processed_dir, "inf_diario_processed.parquet")
                df_inf.to_parquet(output_inf, index=False)
                logging.info(f"Arquivo Parquet salvo em: {output_inf}")
        else:
            logging.warning(f"Arquivo {inf_path} não encontrado.")
            
        logging.info("FASE 2 concluída com sucesso!")

    except Exception as e:
        logging.critical(f"Erro durante o processamento de dados: {e}")

if __name__ == "__main__":
    run_processing()