import re

def parse_robot_file(file_path):
    """
    Lê um arquivo .robot e extrai blocos de Feature que estão comentados.
    Cada Feature deve começar com '# Feature' e continuar até a próxima Feature ou fim do arquivo.
    Retorna uma lista de strings, cada uma representando um Feature completo.
    """

    features = []         # Lista final de features encontrados
    current_feature = []  # Acumulador temporário do feature atual
    inside_feature = False

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Se a linha começa com "# Feature", iniciamos um novo bloco
            if stripped.lower().startswith("# feature"):
                # Se já estávamos dentro de outro feature, salvamos ele
                if current_feature:
                    features.append("\n".join(current_feature))
                    current_feature = []

                inside_feature = True
                # Adiciona a linha sem o "#" inicial
                current_feature.append(stripped.lstrip("#").strip())

            # Se já estamos dentro de um bloco de Feature
            elif inside_feature:
                if stripped.startswith("#"):
                    # Remove o "#" e adiciona ao bloco
                    current_feature.append(stripped.lstrip("#").strip())
                elif stripped == "":
                    # Linha em branco → mantém para espaçamento
                    current_feature.append("")
                else:
                    # Encontramos código normal (não comentado) → fechamos o bloco
                    if current_feature:
                        features.append("\n".join(current_feature))
                        current_feature = []
                    inside_feature = False

        # Se o arquivo terminou enquanto ainda estávamos dentro de um Feature
        if current_feature:
            features.append("\n".join(current_feature))

    return features
