# services/feature_service.py - VERSÃO ROBUSTA RECOMENDADA

import os
from typing import List, Dict, Any, Tuple

from core.parser import extract_scenarios_from_robot_file

def process_robot_files(robot_files: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    # Cole aqui a sua função process_robot_files que já estava funcionando
    all_scenarios_data = []
    total_scenarios_found = 0
    for file_path in robot_files:
        try:
            scenarios, stats = extract_scenarios_from_robot_file(file_path)
            if scenarios:
                all_scenarios_data.extend(scenarios)
                total_scenarios_found += stats.get("scenarios", 0)
        except Exception as e:
            print(f"Error processing file '{file_path}': {e}")
    final_stats = { "files_processed": len(robot_files), "scenarios_extracted": total_scenarios_found }
    return all_scenarios_data, final_stats

def build_feature_content(scenarios_data: List[Dict[str, Any]], project_key: str, global_tags_str: str) -> Tuple[str, Dict[str, Any]]:
    """
    Constrói o conteúdo do .feature e um mapa de posições para cada cenário
    usando um método robusto de junção de strings.
    """
    if not scenarios_data:
        return "No scenarios found.", {}

    header_parts = []
    if project_key:
        header_parts.append(project_key)
    header_parts.append("Feature: Testes automatizados gerados pela aplicação Hobgoblin")
    header = "\n".join(header_parts)

    scenario_blocks = []
    global_tags = global_tags_str.split()
    for scenario in scenarios_data:
        block_parts = []
        detected_tags = scenario.get('detected_tags', [])
        all_tags = sorted(list(set(global_tags + detected_tags)))
        
        if all_tags:
            block_parts.append(" ".join(all_tags))
        
        scenario_text = scenario.get('text', '# Scenario not found')
        block_parts.append(scenario_text)
        
        scenario_blocks.append("\n".join(block_parts))

    final_content = header + "\n\n" + "\n\n".join(scenario_blocks)

    positions_map = {}
    current_pos = len(header) + 2
    for i, scenario in enumerate(scenarios_data):
        block_len = len(scenario_blocks[i])
        start_pos = current_pos
        end_pos = start_pos + block_len
        positions_map[scenario['id']] = {'start': start_pos, 'end': end_pos}
        current_pos = end_pos + 2

    return final_content, positions_map

def save_feature_file(file_path: str, content: str) -> None:
    # Cole aqui a sua função save_feature_file que já estava funcionando
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except IOError as e:
        raise IOError(f"Failed to write to file {file_path}: {e}")