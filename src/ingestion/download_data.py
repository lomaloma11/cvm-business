import os
import sys
import logging
import zipfile
import io

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from cvm_client import CVMClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_ingestion():
    client = CVMClient()
    
    files_to_download = {
        "informe_diario_zip": "FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_202401.zip",
        "cadastro_fundos": "FI/CAD/DADOS/cad_fi.csv"
    }

    logging.info("Iniciando processo de ingestão de dados brutos da CVM...")
    
    for key, relative_path in files_to_download.items():
        logging.info(f"Baixando dataset CVM: '{key}'...")
        
        try:
            raw_data = client.fetch_file_content(relative_path=relative_path)
            
            # Se for um arquivo ZIP, extrai o CSV contido nele
            if relative_path.endswith(".zip"):
                logging.info(f"Descompactando arquivo ZIP: {relative_path}")
                with zipfile.ZipFile(io.BytesIO(raw_data)) as z:
                    z.extractall(client.download_dir)
                logging.info("Arquivo CSV extraído com sucesso do ZIP!")
            else:
                original_filename = relative_path.split("/")[-1]
                client.save_raw_file(raw_data, original_filename)
            
        except Exception as e:
            logging.error(f"Falha ao baixar dataset CVM '{key}'. Motivo: {e}")

    logging.info("Processo de ingestão da CVM finalizado.")

if __name__ == "__main__":
    run_ingestion()