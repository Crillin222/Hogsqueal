def parse_robot_file(path):
    """
    Lê um arquivo .robot e extrai blocos comentados de Feature/Scenario.
    Retorna uma lista de strings, cada uma representando uma Feature completa.
    """
    features = []
    current_block = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            # Remove espaços extras no começo/fim
            stripped = line.strip()

            # Considerar apenas linhas comentadas com "#"
            if stripped.startswith("#"):
                # Remove o "#" e tira espaços extras
                uncommented = stripped.lstrip("#").strip()
                if uncommented:  # ignora linhas só com "#"
                    current_block.append(uncommented)
            else:
                # Se encontramos uma linha não comentada e temos um bloco em andamento
                if current_block:
                    features.append("\n".join(current_block))
                    current_block = []

        # Se acabar o arquivo e ainda tiver um bloco em andamento
        if current_block:
            features.append("\n".join(current_block))

    return features
