import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def validate_dataframe(df: pd.DataFrame, dataset_name: str, key_column: str) -> bool:
    """Executa checagens básicas de qualidade de dados."""
    logging.info(f"Iniciando validação de qualidade para: {dataset_name}")
    
    # Checagem de dataset vazio
    if df.empty:
        logging.error(f"Validação FALHOU: O dataset {dataset_name} está vazio!")
        return False
        
    # Checagem de nulos na chave primária
    null_keys = df[key_column].isnull().sum()
    if null_keys > 0:
        logging.error(f"Validação FALHOU: Encontrados {null_keys} valores nulos na chave '{key_column}'.")
        return False
        
    # Checagem de duplicidades críticas na chave
    if dataset_name == "Cadastro Fundos":
        duplicates = df.duplicated(subset=[key_column]).sum()
        if duplicates > 0:
            logging.error(f"Validação FALHOU: Encontradas {duplicates} duplicatas de CNPJ no Cadastro!")
            return False

    logging.info(f"Validação de qualidade do dataset '{dataset_name}' APROVADA sem erros!")
    return True