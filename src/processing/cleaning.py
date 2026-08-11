import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def clean_cadastro_fundos(filepath: str) -> pd.DataFrame:
    """Limpa e padroniza o arquivo de Cadastro de Fundos (cad_fi.csv)."""
    logging.info("Iniciando limpeza do Cadastro de Fundos...")
    
    # Leitura com encoding latino
    df = pd.read_csv(filepath, sep=";", encoding="ISO-8859-1", dtype=str)
    
    # Remove caractere invisível BOM (\ufeff), espaços e padroniza para maiúsculo sem usar regex
    df.columns = df.columns.astype(str).str.lstrip('\ufeff').str.strip().str.upper()
    
    # Filtrar apenas fundos em funcionamento normal
    if "SIT" in df.columns:
        df = df[df["SIT"] == "EM FUNCIONAMENTO NORMAL"].copy()
        
    # Seleção de colunas estratégicas para o modelo dimensional
    cols_to_keep = [
        "CNPJ_FUNDO", "DENOM_SOCIAL", "CLASSE", "TP_FUNDO", 
        "PUBLICO_ALVO", "ADMIN", "GESTOR", "SG_UF", "MUNICIPIO"
    ]
    existing_cols = [c for c in cols_to_keep if c in df.columns]
    df = df[existing_cols]
    
    # Limpeza de nulos e duplicações por CNPJ
    df["CNPJ_FUNDO"] = df["CNPJ_FUNDO"].str.replace(r"\D", "", regex=True) # Apenas números
    df = df.drop_duplicates(subset=["CNPJ_FUNDO"])
    df = df.fillna("NÃO INFORMADO")
    
    logging.info(f"Cadastro limpo com sucesso. Registros ativos: {len(df)}")
    return df


def clean_informe_diario(filepath: str) -> pd.DataFrame:
    """Limpa e padroniza o arquivo de Informes Diários (inf_diario_fi_202401.csv)."""
    logging.info("Iniciando limpeza do Informe Diário...")
    
    df = pd.read_csv(filepath, sep=";", encoding="ISO-8859-1")
    
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

    # Seleção de colunas para a Tabela Fato
    cols_fato = ["CNPJ_FUNDO", "DT_COMPTC", "VL_TOTAL", "VL_QUOTA", "VL_PATRIM_LIQ", "CAPTC_DIA", "RESG_DIA", "NR_COTST"]
    df = df[[c for c in cols_fato if c in df.columns]].copy()
    
    # Tratamento de tipos
    df["CNPJ_FUNDO"] = df["CNPJ_FUNDO"].astype(str).str.replace(r"\D", "", regex=True)
    df["DT_COMPTC"] = pd.to_datetime(df["DT_COMPTC"], errors="coerce")
    
    # Conversão de colunas numéricas
    numeric_cols = ["VL_TOTAL", "VL_QUOTA", "VL_PATRIM_LIQ", "CAPTC_DIA", "RESG_DIA", "NR_COTST"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            
    # Criação de métrica derivada: Captação Líquida Diária (Captação - Resgate)
    df["CAPT_LIQUIDA_DIA"] = df["CAPTC_DIA"] - df["RESG_DIA"]
    
    # Remoção de registros inválidos (sem data ou sem CNPJ)
    df = df.dropna(subset=["CNPJ_FUNDO", "DT_COMPTC"])
    df = df.drop_duplicates(subset=["CNPJ_FUNDO", "DT_COMPTC"])
    
    logging.info(f"Informe Diário limpo com sucesso. Registros diários: {len(df)}")
    return df