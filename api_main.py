# api_main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

# Importa as funções dos nossos serviços que já estão funcionando!
from services.file_service import find_robot_files
from services.feature_service import process_robot_files

# --- 1. Inicializa a aplicação FastAPI ---
app = FastAPI(
    title="Hobgoblin API",
    description="Backend para a aplicação Hobgoblin, que processa arquivos .robot.",
    version="1.0.0"
)

# --- 2. Define os "Modelos de Dados" para a API ---
# Isso diz ao FastAPI como os dados que chegam devem se parecer.
# É uma forma de validação automática.
class ScanRequest(BaseModel):
    folder_path: str
    include_subfolders: bool

# --- 3. Cria os "Endpoints" da API ---

# Endpoint raiz para teste de saúde.
@app.get("/")
async def read_root():
    """Endpoint principal para verificar se a API está no ar."""
    return {"message": "Hobgoblin API está funcionando!"}

# Endpoint para escanear uma pasta e processar os arquivos.
@app.post("/scan-folder/")
async def scan_folder(request: ScanRequest) -> Dict[str, Any]:
    """
    Recebe um caminho de pasta, escaneia por arquivos .robot, 
    extrai os cenários e retorna os dados processados.
    """
    try:
        # Reutiliza a lógica que já construímos!
        robot_files = find_robot_files(request.folder_path, request.include_subfolders)
        scenarios_data, stats = process_robot_files(robot_files)

        return {
            "success": True,
            "data": {
                "scenarios": scenarios_data,
                "stats": stats
            }
        }
    except Exception as e:
        # Se algo der errado, retorna uma mensagem de erro clara.
        return {"success": False, "error": str(e)}