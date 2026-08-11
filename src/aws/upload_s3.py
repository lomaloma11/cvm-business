import os
import sys
import logging
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class S3Uploader:
    """Classe para gerenciar uploads de arquivos Parquet para o AWS S3."""
    
    def __init__(self):
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket_name = os.getenv("S3_BUCKET_NAME")

        if not self.access_key or not self.secret_key or not self.bucket_name:
            raise ValueError("Credenciais AWS ou nome do Bucket S3 não configurados no arquivo .env!")

        # Inicializa o cliente boto3 com as credenciais
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )

    def upload_file(self, local_file_path: str, s3_prefix: str = "processed/cvm") -> bool:
        """
        Envia um arquivo local para a pasta/prefixo correspondente no S3.
        """
        if not os.path.exists(local_file_path):
            logging.error(f"Arquivo local não encontrado: {local_file_path}")
            return False

        filename = os.path.basename(local_file_path)
        s3_key = f"{s3_prefix.strip('/')}/{filename}"

        logging.info(f"Iniciando upload de '{filename}' para 's3://{self.bucket_name}/{s3_key}'...")

        try:
            self.s3_client.upload_file(local_file_path, self.bucket_name, s3_key)
            logging.info(f"Upload do arquivo '{filename}' concluído com sucesso no S3!")
            return True
        except ClientError as e:
            logging.error(f"Erro do cliente AWS S3 durante o upload: {e}")
            return False
        except NoCredentialsError:
            logging.error("Credenciais AWS não encontradas ou inválidas.")
            return False


def run_s3_upload():
    processed_dir = "data/processed/cvm"
    
    if not os.path.exists(processed_dir):
        logging.error(f"Diretório de dados processados '{processed_dir}' não existe.")
        return

    try:
        uploader = S3Uploader()
        
        # Envia todos os arquivos .parquet da pasta processed
        for file in os.listdir(processed_dir):
            if file.endswith(".parquet"):
                local_path = os.path.join(processed_dir, file)
                uploader.upload_file(local_path, s3_prefix="processed/cvm")
                
        logging.info("Upload para o AWS S3 concluído!")

    except Exception as e:
        logging.critical(f"Falha na execução do upload S3: {e}")

if __name__ == "__main__":
    run_s3_upload()