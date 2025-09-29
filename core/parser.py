import re
import resources_rc
resources_rc.qInitResources()

def extract_scenarios_from_robot_file(file_path):
    """
    Lê um arquivo .robot e extrai os blocos de Cenário Gherkin comentados.
    Esta versão é robusta contra diferentes tipos de espaçamento e caracteres
    invisíveis (como o No-Break Space, U+00A0).

    Args:
        file_path (str): O caminho para o arquivo .robot.

    Returns:
        A tuple containing:
        - scenarios (list[str]): Uma lista de strings, onde cada string é um cenário completo e descomentado.
        - stats (dict): Um dicionário com a contagem de cenários encontrados.
    """
    scenarios = []
    current_scenario_lines = []
    found_feature_context = False
    scenario_count = 0

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # ETAPA DE LIMPEZA: Normaliza espaços e remove o caractere invisível
                # Substitui o caractere especial (U+00A0) por um espaço normal
                cleaned_line = line.replace('\u00A0', ' ')
                
                # Remove espaços no início e no fim da linha
                stripped_line = cleaned_line.strip()

                # Se a linha não começar com '#', não é Gherkin comentado.
                if not stripped_line.startswith("#"):
                    # Se a linha não for vazia, consideramos que o bloco Gherkin acabou.
                    if stripped_line:
                        found_feature_context = False
                    continue

                # Remove o '#' e espaços extras do início para análise do conteúdo
                # Ex: "#   Scenario:" vira "Scenario:"
                content_line = stripped_line.lstrip("#").strip()

                # Procura pelo início de um contexto de feature
                if content_line.lower().startswith("feature"):
                    found_feature_context = True
                    continue

                if not found_feature_context:
                    continue

                # Detecta o início de um novo cenário
                if content_line.lower().startswith("scenario"):
                    if current_scenario_lines:
                        scenarios.append("\n".join(current_scenario_lines))
                    
                    scenario_count += 1
                    current_scenario_lines = [content_line]
                
                # Se já iniciamos um cenário, adiciona as linhas seguintes
                elif current_scenario_lines and content_line:
                    current_scenario_lines.append(content_line)

            # Garante que o último cenário do arquivo seja adicionado
            if current_scenario_lines:
                scenarios.append("\n".join(current_scenario_lines))

    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
        return [], {"scenarios": 0}

    stats = {
        "scenarios": scenario_count
    }
    return scenarios, stats