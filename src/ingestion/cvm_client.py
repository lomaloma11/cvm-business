import os
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class CVMClient:
    """Cliente resiliente para download de dados abertos da CVM (Comissão de Valores Mobiliários)."""
    
    BASE_URL = "https://dados.cvm.gov.br/dados"

    def __init__(self, download_dir: str = "data/raw/cvm"):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        
        self.session = requests.Session()
        retry_strategy = Retry(
            total=4,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*"
        }

    def fetch_file_content(self, relative_path: str) -> bytes:
        """
        Realiza requisição GET para baixar um arquivo do portal de dados abertos da CVM.
        
        :param relative_path: Caminho relativo do arquivo (ex: 'FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_202401.csv')
        :return: Conteúdo bruto do arquivo em bytes
        """
        url = f"{self.BASE_URL}/{relative_path.lstrip('/')}"
        logging.info(f"Iniciando download CVM de: {url}")
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=60)
            response.raise_for_status()
            logging.info("Download concluído com sucesso.")
            return response.content
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"Erro HTTP ao baixar {relative_path}: {http_err}")
            raise
        except requests.exceptions.RequestException as err:
            logging.error(f"Erro de conexão ao baixar {relative_path}: {err}")
            raise

    def save_raw_file(self, content: bytes, filename: str) -> str:
        """Salva o conteúdo bruto no diretório RAW da CVM."""
        file_path = os.path.join(self.download_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        logging.info(f"Arquivo RAW salvo com sucesso em: {file_path}")
        return file_path