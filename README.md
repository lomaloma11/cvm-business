## Arquitetura da Solução

```mermaid
flowchart LR
    %% Fonte
    subgraph S1["1. Origem dos Dados"]
        A1["Portal CVM<br>• cad_fi.csv<br>• inf_diario_fi.csv"]
    end

    %% ETL Python
    subgraph S2["2. Processamento (Python)"]
        B1["cleaning.py<br>• Regex / Encoding<br>• Conversão Numérica"]
        B2["transformations.py<br>• Formato Parquet"]
        B1 --> B2
    end

    %% Data Lake
    subgraph S3["3. Data Lake (AWS S3)"]
        C1["Bucket S3 (Processed)<br>• cad_fi.parquet<br>• inf_diario.parquet"]
    end

    %% Data Warehouse
    subgraph S4["4. Data Warehouse (PostgreSQL)"]
        direction TB
        D1[("dim_fund")]
        D2[("dim_date")]
        D3[("fact_informe_diario")]
        D1 -->|1 : N| D3
        D2 -->|1 : N| D3
    end

    %% Conexões
    A1 -->|Leitura CSV| B1
    B2 -->|upload_s3.py| C1
    C1 -->|load_postgres.py| S4
```

---

## Features / Funcionalidades

* **Pipeline ETL Resiliente:** Tratamento avançado de encoding (`ISO-8859-1`), remoção de espaços invisíveis e caracteres ocultos com expressões regulares (`Regex`).
* **Ingestão Otimizada com Parquet:** Conversão colunar reduzindo o tempo de I/O e os custos de armazenamento no AWS S3.
* **Modelagem Dimensional (Star Schema):** Estrutura no PostgreSQL com tabelas de dimensão (`dim_fund`, `dim_date`) e fato (`fact_informe_diario`) com validação de integridade referencial.
* **Auditoria e Logs:** Registro estruturado de execução via módulo `logging` para monitoramento de volume e consistência de dados em cada etapa.
