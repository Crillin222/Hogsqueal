# core/parser.py

import os
import re
from typing import List, Dict, Any, Tuple
import uuid

def _extract_scenario_name(scenario_text: str) -> str:
    """Helper para extrair o nome de um cenário do seu texto completo."""
    match = re.search(r"Scenario(?: Outline)?:(.*)", scenario_text, re.IGNORECASE)
    return match.group(1).strip() if match else "Unnamed Scenario"

def extract_scenarios_from_robot_file(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Lê um arquivo .robot e extrai blocos de Cenário Gherkin comentados,
    retornando uma estrutura de dados rica para cada um.
    """
    scenarios_data = []
    current_scenario_lines = []
    captured_tags = []
    
    in_test_cases_section = False
    current_robot_test_case = "Unknown Test Case"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # ### LÓGICA DE CORREÇÃO ###
                # Mantemos a linha original com espaços à esquerda para checar a indentação
                original_line = line.replace('\u00A0', ' ')
                cleaned_line = original_line.strip()

                if cleaned_line.lower().startswith("*** test cases ***"):
                    in_test_cases_section = True
                    continue
                if cleaned_line.lower().startswith("***"):
                    in_test_cases_section = False
                    continue
                
                # Se estamos na seção de testes e a linha NÃO é um comentário...
                if in_test_cases_section and not cleaned_line.startswith("#"):
                    # ...e a linha NÃO começa com espaço (não é indentada), então é um nome de Test Case!
                    if cleaned_line and not original_line.startswith((' ', '\t')):
                        current_robot_test_case = cleaned_line
                
                if not cleaned_line.startswith("#"):
                    continue

                content_line = cleaned_line.lstrip("#").strip()

                if content_line.startswith("@"):
                    captured_tags.extend(content_line.split())
                    continue

                if content_line.lower().startswith(("scenario", "cenário")):
                    if current_scenario_lines:
                        full_text = "\n".join(current_scenario_lines)
                        scenario_obj = {
                            "id": str(uuid.uuid4()),
                            "name": _extract_scenario_name(full_text),
                            "text": full_text,
                            "source_file": os.path.basename(file_path),
                            "robot_test_case": current_robot_test_case,
                            "detected_tags": captured_tags
                        }
                        scenarios_data.append(scenario_obj)
                    
                    current_scenario_lines = [content_line]
                    captured_tags = []
                
                elif current_scenario_lines and content_line:
                    current_scenario_lines.append(content_line)

            if current_scenario_lines:
                full_text = "\n".join(current_scenario_lines)
                scenario_obj = {
                    "id": str(uuid.uuid4()),
                    "name": _extract_scenario_name(full_text),
                    "text": full_text,
                    "source_file": os.path.basename(file_path),
                    "robot_test_case": current_robot_test_case,
                    "detected_tags": captured_tags
                }
                scenarios_data.append(scenario_obj)

    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
        return [], {"scenarios": 0}

    stats = {
        "scenarios": len(scenarios_data)
    }
    return scenarios_data, stats