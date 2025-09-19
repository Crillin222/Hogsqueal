import re

def parse_robot_file(file_path):
    """
    Lê um arquivo .robot e extrai blocos de Feature que estão comentados.
    Cada Feature começa com '# Feature' e continua até a próxima Feature ou o fim do arquivo.
    
    Retorna:
    - features: lista de strings (cada feature completo)
    - stats: dicionário com contagem de features e cenários
    """

    features = []         # Lista final de features encontrados
    current_feature = []  # Acumulador temporário do feature atual
    inside_feature = False

    feature_count = 0
    scenario_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Detecta início de um Feature
            if stripped.lower().startswith("# feature"):
                if current_feature:
                    features.append("\n".join(current_feature))
                    current_feature = []

                inside_feature = True
                feature_count += 1
                current_feature.append(stripped.lstrip("#").strip())

            # Dentro de um Feature
            elif inside_feature:
                if stripped.startswith("#"):
                    content = stripped.lstrip("#").strip()
                    current_feature.append(content)

                    # Conta cenários
                    if content.lower().startswith("scenario"):
                        scenario_count += 1

                elif stripped == "":
                    current_feature.append("")
                else:
                    # Linha fora de comentário → fecha feature
                    if current_feature:
                        features.append("\n".join(current_feature))
                        current_feature = []
                    inside_feature = False

        # Se terminou ainda dentro de um Feature
        if current_feature:
            features.append("\n".join(current_feature))

    stats = {
        "features": feature_count,
        "scenarios": scenario_count
    }

    return features, stats
