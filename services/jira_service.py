# services/jira_service.py

import requests
import json
import os
from typing import Union, Tuple, List, Dict, Any

# URL base do seu Jira (extraído do seu código anterior)
JIRA_BASE_URL = "https://jerry.dieboldnixdorf.com"

def get_auth_headers(login_config: dict) -> Tuple[Union[tuple, None], dict]:
    """
    Prepara a autenticação para a biblioteca requests.
    Retorna uma tupla: (auth_object_for_requests, headers_dict)
    """
    if login_config.get("login_type") == "userpass":
        # Retorna tupla para Basic Auth
        return (login_config["user"], login_config["token"]), {}
    else:
        # Retorna None para auth e um dicionário de header para Bearer Token
        return None, {"Authorization": f"Bearer {login_config['token']}"}

def import_feature_to_xray(file_path: str, project_key: str, login_config: dict) -> List[Dict[str, Any]]:
    """
    Envia o arquivo .feature para o Xray.
    Retorna a lista de testes criados/atualizados (resposta JSON do Xray).
    """
    url = f"{JIRA_BASE_URL}/rest/raven/2.0/import/feature?projectKey={project_key}"
    
    auth, headers = get_auth_headers(login_config)
    
    # Abre o arquivo em modo binário para envio
    with open(file_path, 'rb') as f:
        files = {'file': f}
        
        try:
            response = requests.post(url, auth=auth, headers=headers, files=files)
            response.raise_for_status() # Levanta erro se não for 200 OK
            
            # O Xray geralmente retorna uma lista de objetos JSON com as chaves dos testes
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # Captura erros de conexão, 404, 401, 500, etc.
            error_msg = f"Connection Failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nServer Response: {e.response.text}"
            raise Exception(error_msg)

def update_issue_description(issue_key: str, description: str, login_config: dict) -> bool:
    """
    Atualiza a descrição de uma issue no Jira (para o teste de conexão).
    """
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}"
    auth, headers = get_auth_headers(login_config)
    
    # Adiciona o content-type JSON aos headers
    headers["Content-Type"] = "application/json"
    
    payload = {
        "fields": {
            "description": description
        }
    }
    
    try:
        response = requests.put(url, auth=auth, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to update issue: {str(e)}")