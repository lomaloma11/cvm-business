```mermaid
flowchart LR
    %% Fontes
    subgraph S1["1. Fonte de Dados (Raw)"]
        A1["Portal CVM<br>• cad_fi.csv<br>• inf_diario_fi.csv"]
    end

    %% Pipeline Python
    subgraph S2["2. Processamento & ETL (Python)"]
        B1["cleaning.py<br>• Regex / Encoding<br>• Tratamento de Tipos"]
        B2["transformations.py<br>• Conversão Parquet"]
        B1 --> B2
    end

    %% Data Lake AWS
    subgraph S3["3. Data Lake (AWS S3)"]
        C1["Bucket S3 (Processed)<br>• cad_fi.parquet<br>• inf_diario.parquet"]
    end

    %% Data Warehouse Postgres
    subgraph S4["4. Data Warehouse (PostgreSQL)"]
        direction TB
        D1[("dim_fund")]
        D2[("dim_date")]
        D3[("fact_informe_diario")]
        D1 -->|1 : N| D3
        D2 -->|1 : N| D3
    end

    %% Visualização
    subgraph S5["5. Business Intelligence"]
        E1["Power BI Dashboard<br>• Regras DAX<br>• KPIs de Mercado"]
    end

    %% Conexões
    A1 -->|Leitura CSV| B1
    B2 -->|upload_s3.py| C1
    C1 -->|load_postgres.py| S4
    S4 -->|Consulta SQL| E1
