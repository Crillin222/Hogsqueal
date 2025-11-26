import os
from typing import List, Dict, Any, Tuple

from core.parser import extract_scenarios_from_robot_file

def process_robot_files(robot_files: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Processes a list of .robot files to extract scenarios and statistics.

    Args:
        robot_files (List[str]): List of file paths to .robot files.

    Returns:
        Tuple[List[Dict[str, Any]], Dict[str, Any]]: A tuple containing:
            - A list of dictionaries, where each dictionary represents an extracted scenario.
            - A dictionary with processing statistics (e.g., total files, total scenarios).
    """
    all_scenarios_data = []
    total_scenarios_found = 0
    
    for file_path in robot_files:
        try:
            # Extract scenarios from individual file using the parser
            scenarios, stats = extract_scenarios_from_robot_file(file_path)
            if scenarios:
                all_scenarios_data.extend(scenarios)
                total_scenarios_found += stats.get("scenarios", 0)
        except Exception as e:
            print(f"Error processing file '{file_path}': {e}")
            
    final_stats = {
        "files_processed": len(robot_files),
        "scenarios_extracted": total_scenarios_found
    }
    
    return all_scenarios_data, final_stats

def build_feature_content(scenarios_data: List[Dict[str, Any]], 
                          global_tags_str: str, 
                          active_tags: List[str]) -> Tuple[str, Dict[str, Any]]:
    """
    Builds the content for the .feature file based on the extracted scenarios and tag configurations.

    Args:
        scenarios_data (List[Dict[str, Any]]): List of scenario data dictionaries.
        global_tags_str (str): String containing global tags separated by spaces.
        active_tags (List[str]): List of tags that are currently active/enabled in the UI.

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple containing:
            - The formatted .feature file content as a string.
            - A dictionary mapping scenario IDs to their start and end character positions in the content.
    """
    if not scenarios_data:
        return "No scenarios found.", {}

    # Fixed header for the feature file
    header = "Feature: Testes automatizados gerados pela aplicação Hobgoblin"
    
    scenario_blocks = []
    global_tags = global_tags_str.split()

    for scenario in scenarios_data:
        block_parts = []
        
        # --- Tag Collection Logic ---
        detected = scenario.get('detected_tags', {})
        force_tags = detected.get('force', [])
        case_tags = detected.get('case', [])
        additional_tags = scenario.get('additional_tags', '').split()
        
        # Combine all potential tags from different sources into a unique set
        all_potential_tags = set(global_tags + force_tags + case_tags + additional_tags)
        
        # Filter tags: Keep if it's in the active list OR if it's a global tag
        final_tags = sorted([
            tag for tag in all_potential_tags 
            if tag in active_tags or tag in global_tags
        ])
        
        # Add tags line if any tags remain after filtering
        if final_tags:
            block_parts.append(" ".join(final_tags))
        
        # Add the scenario text itself
        block_parts.append(scenario.get('text', '# Scenario not found'))
        
        # Join parts of this scenario block
        scenario_blocks.append("\n".join(block_parts))

    # Combine header and all scenario blocks with double newlines
    final_content = header + "\n\n" + "\n\n".join(scenario_blocks)

    # --- Position Mapping Logic ---
    # Calculate start and end positions for each scenario to support UI highlighting
    positions_map = {}
    # Initial position is after header + 2 newlines
    current_pos = len(header) + 2 
    
    for i, scenario in enumerate(scenarios_data):
        block_len = len(scenario_blocks[i])
        
        start_pos = current_pos
        end_pos = start_pos + block_len
        
        positions_map[scenario['id']] = {'start': start_pos, 'end': end_pos}
        
        # Update current position for the next iteration (block length + 2 newlines separator)
        current_pos = end_pos + 2

    return final_content, positions_map

def save_feature_file(file_path: str, content: str) -> None:
    """
    Saves the generated content to a file.

    Args:
        file_path (str): The full path where the file should be saved.
        content (str): The content to write to the file.

    Raises:
        IOError: If writing to the file fails.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except IOError as e:
        raise IOError(f"Failed to write to file {file_path}: {e}")