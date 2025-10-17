# core/parser.py - VERSÃO FINAL COM PARSER DE TAGS CORRIGIDO

import os
import re
from typing import List, Dict, Any, Tuple
import uuid

def _extract_scenario_name(scenario_text: str) -> str:
    """Helper para extrair o nome de um cenário do seu texto completo."""
    match = re.search(r"Scenario(?: Outline)?:(.*)", scenario_text, re.IGNORECASE)
    return match.group(1).strip() if match else "Unnamed Scenario"

def extract_scenarios_from_robot_file(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    scenarios_data = []
    current_scenario_lines = []
    
    in_settings_section, in_test_cases_section = False, False
    force_tags, case_tags, gherkin_tags = [], [], []
    current_test_case = "Unknown Test Case"

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            original_line = line.replace('\u00A0', ' ')
            cleaned_line = original_line.strip()

            def save_previous_scenario():
                if current_scenario_lines:
                    full_text = "\n".join(current_scenario_lines)
                    final_case_tags = case_tags + gherkin_tags
                    scenarios_data.append({
                        "id": str(uuid.uuid4()), "name": _extract_scenario_name(full_text),
                        "text": full_text, "source_file": os.path.basename(file_path),
                        "robot_test_case": current_test_case,
                        "detected_tags": {"force": force_tags, "case": final_case_tags}
                    })
                    current_scenario_lines.clear()

            if cleaned_line.lower().startswith("*** settings ***"):
                in_settings_section, in_test_cases_section = True, False
                continue
            if cleaned_line.lower().startswith("*** test cases ***"):
                in_settings_section, in_test_cases_section = False, True
                continue
            if cleaned_line.lower().startswith("***"):
                in_settings_section, in_test_cases_section = False, False
                continue

            if in_settings_section and cleaned_line.lower().startswith("force tags"):
                force_tags.extend(re.split(r'\s{2,}', cleaned_line, 1)[1].split())

            if in_test_cases_section:
                if cleaned_line and not original_line.startswith((' ', '\t', '#')):
                    save_previous_scenario()
                    current_test_case = cleaned_line
                    case_tags, gherkin_tags = [], []

                if cleaned_line.lower().startswith("[tags]"):
                    case_tags.extend(re.split(r'\s{2,}', cleaned_line, 1)[1].split())

            if cleaned_line.startswith("#"):
                content_line = cleaned_line.lstrip("#").strip()
                if content_line:
                    if content_line.startswith("@"):
                        gherkin_tags.extend(content_line.split())
                    elif content_line.lower().startswith(("scenario", "cenário")):
                        save_previous_scenario()
                        current_scenario_lines.append(content_line)
                    elif current_scenario_lines:
                        current_scenario_lines.append(content_line)

    save_previous_scenario() # Salva o último cenário do arquivo
    return scenarios_data, {"scenarios": len(scenarios_data)}