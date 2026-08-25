import pandas as pd
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def validate_cadastro_fundos(df: pd.DataFrame) -> bool:
    """Valida integridade e regras de negócio do Cadastro de Fundos (dim_fund)."""
    logging.info("Iniciando validação de qualidade: Cadastro de Fundos...")
    errors = []

    # Dataset vazio
    if df.empty:
        logging.error("Validação FALHOU: DataFrame de Cadastro de Fundos está vazio.")
        return False

    # Chave primária (CNPJ_FUNDO)
    if "CNPJ_FUNDO" not in df.columns:
        errors.append("Coluna 'CNPJ_FUNDO' não encontrada.")
    else:
        if df["CNPJ_FUNDO"].isnull().any():
            errors.append("Existem valores nulos em CNPJ_FUNDO.")
        if df.duplicated(subset=["CNPJ_FUNDO"]).any():
            errors.append("Existem duplicatas de CNPJ no Cadastro de Fundos.")
        if (df["CNPJ_FUNDO"].str.len() != 14).any():
            errors.append("Existem CNPJs com tamanho diferente de 14 dígitos.")

    if errors:
        logging.error("Validação do Cadastro de Fundos REPROVADA:")
        for err in errors:
            logging.error(f"  • {err}")
        return False

    logging.info("Validação do Cadastro de Fundos APROVADA com sucesso!")
    return True

def validate_informe_diario(df: pd.DataFrame) -> bool:
    """Valida chave composta, tipos e regras numéricas do Informe Diário (fact_informe_diario)."""
    logging.info("Iniciando validação de qualidade: Informe Diário...")
    errors = []

    # Dataset vazio
    if df.empty:
        logging.error("Validação FALHOU: DataFrame de Informe Diário está vazio.")
        return False

    # Chave Composta (CNPJ_FUNDO + DT_COMPTC)
    pk_cols = ["CNPJ_FUNDO", "DT_COMPTC"]
    for col in pk_cols:
        if col not in df.columns:
            errors.append(f"Coluna de chave primária '{col}' não encontrada.")
        elif df[col].isnull().any():
            errors.append(f"Valores nulos encontrados na coluna de chave '{col}'.")

    if all(c in df.columns for c in pk_cols):
        if df.duplicated(subset=pk_cols).any():
            errors.append("Duplicatas encontradas na chave primária composta (CNPJ_FUNDO + DT_COMPTC).")
        if not np.issubdtype(df["DT_COMPTC"].dtype, np.datetime64):
            errors.append("Coluna 'DT_COMPTC' não está no formato Datetime.")

    # Regras de Negócio Financeiras (Estoque > 0 e Fluxo >= 0)
    if "VL_QUOTA" in df.columns and (df["VL_QUOTA"] <= 0).any():
        errors.append("Existem registros com VL_QUOTA <= 0.")
    if "VL_PATRIM_LIQ" in df.columns and (df["VL_PATRIM_LIQ"] <= 0).any():
        errors.append("Existem registros com VL_PATRIM_LIQ <= 0.")
    if "CAPTC_DIA" in df.columns and (df["CAPTC_DIA"] < 0).any():
        errors.append("Existem registros com CAPTC_DIA negativo.")
    if "RESG_DIA" in df.columns and (df["RESG_DIA"] < 0).any():
        errors.append("Existem registros com RESG_DIA negativo.")

    if errors:
        logging.error("Validação do Informe Diário REPROVADA:")
        for err in errors:
            logging.error(f"  • {err}")
        return False

    logging.info("Validação do Informe Diário APROVADA com sucesso!")
    return True