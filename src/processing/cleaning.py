import pandas as pd
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def clean_cadastro_fundos(filepath: str) -> pd.DataFrame:
    """Limpa e padroniza o arquivo de Cadastro de Fundos (cad_fi.csv)."""
    logging.info("Iniciando limpeza do Cadastro de Fundos...")
    
    # Leitura com encoding latino
    df = pd.read_csv(filepath, sep=";", encoding="ISO-8859-1", dtype=str)
    logging.info(f"Linhas lidas no CSV original: {len(df)}")
    
    # Remove caractere invisível BOM (\ufeff), espaços e padroniza para maiúsculo sem usar regex
    df.columns = df.columns.astype(str).str.lstrip('\ufeff').str.strip().str.upper()

    if "SG_UF" not in df.columns:
        df["SG_UF"] = "ND"
    if "MUNICIPIO" not in df.columns:
        df["MUNICIPIO"] = "NÃO INFORMADO"

    # Trata a coluna CLASSE garantindo que ela sempre exista e seja preenchida
    if "CLASSE" not in df.columns:
        df["CLASSE"] = df["TP_FUNDO"] if "TP_FUNDO" in df.columns else "NÃO INFORMADO"
    else:
        if "TP_FUNDO" in df.columns:
            df["CLASSE"] = df["CLASSE"].fillna(df["TP_FUNDO"])
            df["CLASSE"] = df["CLASSE"].replace(["", "ND", "NÃO INFORMADO", "NONE", "nan"], None)
            df["CLASSE"] = df["CLASSE"].fillna(df["TP_FUNDO"])
        df["CLASSE"] = df["CLASSE"].fillna("NÃO CLASSIFICADO")  

    # Seleção de colunas estratégicas para o modelo dimensional
    cols_to_keep = [
        "CNPJ_FUNDO", "DENOM_SOCIAL", "CLASSE", "TP_FUNDO", 
        "PUBLICO_ALVO", "ADMIN", "GESTOR", "SG_UF", "MUNICIPIO"
    ]
    df = df[[c for c in cols_to_keep if c in df.columns]].copy()

    for col in ["PUBLICO_ALVO","SG_UF", "MUNICIPIO"]:
        if col in df.columns:
            df[col] = df[col].fillna("Não informado")
    
    # Limpeza de nulos e duplicações por CNPJ
    df["CNPJ_FUNDO"] = df["CNPJ_FUNDO"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)

    # Remove CNPJs inválidos ou zerados
    df = df[(df["CNPJ_FUNDO"] != "00000000000000") & (df["CNPJ_FUNDO"].str.len() == 14)]
    df = df.drop_duplicates(subset=["CNPJ_FUNDO"])
    df = df.fillna("NÃO INFORMADO")

    if df.empty:
        raise ValueError("Cadastro de Fundos vazio após a limpeza.")
    
    logging.info(f"Cadastro limpo com sucesso. Registros ativos: {len(df)}")
    return df


def clean_informe_diario(filepath: str) -> pd.DataFrame:
    """Limpa e padroniza o arquivo de Informes Diários (inf_diario_fi_202401.csv)."""
    logging.info("Iniciando limpeza do Informe Diário...")
    
    df = pd.read_csv(filepath, sep=";", encoding="ISO-8859-1", dtype=str)
    
    # Remove caractere invisível BOM (\ufeff), espaços e força caixa alta
    df.columns = df.columns.astype(str).str.lstrip('\ufeff').str.strip().str.upper()
    
    # Mapeamento para garantir a coluna de CNPJ caso haja variação de nome no arquivo CVM
    possible_cnpj_cols = ["CNPJ_FUNDO", "CNPJ_FUNDO_CLASSE", "CNPJ_FUNDO_EXCL"]
    for col in possible_cnpj_cols:
        if col in df.columns:
            if col != "CNPJ_FUNDO":
                df = df.rename(columns={col: "CNPJ_FUNDO"})
            break

    # Validação de presença das colunas essenciais
    essential_cols = ["CNPJ_FUNDO", "DT_COMPTC"]
    missing = [c for c in essential_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Colunas essenciais {missing} não foram encontradas no Informe Diário. Colunas presentes: {list(df.columns)}")

    # Tratamento de tipos
    df["CNPJ_FUNDO"] = df["CNPJ_FUNDO"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
    df["DT_COMPTC"] = pd.to_datetime(df["DT_COMPTC"], errors="coerce")
    
    # Metricas de estoque/preco
    stock_cols = ["VL_TOTAL", "VL_QUOTA", "VL_PATRIM_LIQ"]
    for col in stock_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        else:
            df[col] = np.nan

    # Metricas de fluxo
    flow_cols = ["CAPTC_DIA", "RESG_DIA", "NR_COTST"]
    for col in flow_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)
        else:
            df[col] = 0.0

    # Remoção de nulos em chaves e métricas de estoque
    df = df.dropna(subset=["CNPJ_FUNDO", "DT_COMPTC"] + stock_cols)

    df = df[(df["VL_TOTAL"] > 0) & (df["VL_QUOTA"] > 0) & (df["VL_PATRIM_LIQ"] > 0)]
    df = df[(df["CAPTC_DIA"] >= 0) & (df["RESG_DIA"] >= 0) & (df["NR_COTST"] >= 0)]
    
    # Criação de métrica derivada: Captação Líquida Diária (Captação - Resgate)
    df["CAPT_LIQUIDA_DIA"] = df["CAPTC_DIA"] - df["RESG_DIA"]

    # Seleção de colunas para a Tabela Fato
    cols_fato = [
        "CNPJ_FUNDO", "DT_COMPTC", "VL_TOTAL", "VL_QUOTA", "VL_PATRIM_LIQ", 
        "CAPTC_DIA", "RESG_DIA", "NR_COTST", "CAPT_LIQUIDA_DIA"
        ]
    df = df[[c for c in cols_fato if c in df.columns]].copy()
    
    # Remoção de registros inválidos (sem data ou sem CNPJ)
    df = df[(df["CNPJ_FUNDO"] != "00000000000000") & (df["CNPJ_FUNDO"].str.len() == 14)]
    df = df.drop_duplicates(subset=["CNPJ_FUNDO", "DT_COMPTC"])

    if df.empty:
        raise ValueError("Informe Diário ficou vazio após a limpeza.")
    
    logging.info(f"Informe Diário limpo com sucesso. Registros diários: {len(df)}")
    return df   