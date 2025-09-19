# core/parser.py

def parse_robot_file(path):
    """
    Lê um arquivo .robot e extrai blocos de comentários que descrevem Features/Scenarios.
    Somente linhas de comentários que fazem parte de um bloco que começa com 'Feature'
    são consideradas. Comentários comuns são ignorados.
    """

    features = []      # Lista final com todas as Features extraídas
    current_block = [] # Acumulador temporário para o bloco atual de comentários
    inside_feature = False  # Flag para indicar se estamos dentro de um bloco válido

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            if stripped.startswith("#"):
                uncommented = stripped.lstrip("#").strip()

                # Se encontramos um "Feature", começa um bloco
                if uncommented.lower().startswith("feature"):
                    if current_block:
                        features.append("\n".join(current_block))
                        current_block = []
                    inside_feature = True
                    current_block.append(uncommented)

                # Se já estamos dentro de um Feature → adiciona linha
                elif inside_feature and uncommented:
                    current_block.append(uncommented)

            else:
                # Linha não comentada → fecha o bloco atual, se houver
                if current_block:
                    features.append("\n".join(current_block))
                    current_block = []
                    inside_feature = False

        # Se terminou o arquivo e ainda tem bloco aberto
        if current_block:
            features.append("\n".join(current_block))

    return features
