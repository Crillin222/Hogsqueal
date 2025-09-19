def parse_robot_file(file_path):
    """
    Lê um arquivo .robot e extrai Features comentadas.
    Conta também quantos 'Scenario' existem.
    Retorna (lista_de_features, total_scenarios).
    """

    features = []
    current_feature = []
    inside_feature = False
    scenarios_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Novo Feature
            if stripped.lower().startswith("# feature"):
                if current_feature:
                    features.append("\n".join(current_feature))
                    current_feature = []
                inside_feature = True
                current_feature.append(stripped.lstrip("#").strip())

            elif inside_feature:
                if stripped.startswith("#"):
                    text = stripped.lstrip("#").strip()
                    current_feature.append(text)

                    # Contagem de Scenario
                    if text.lower().startswith("scenario"):
                        scenarios_count += 1
                elif stripped == "":
                    current_feature.append("")
                else:
                    if current_feature:
                        features.append("\n".join(current_feature))
                        current_feature = []
                    inside_feature = False

        if current_feature:
            features.append("\n".join(current_feature))

    return features, scenarios_count
