# core/parser.py

def parse_robot_file(path):
    """
    Lê um arquivo .robot e extrai blocos de comentários
    que descrevem Features/Scenarios no estilo Gherkin.

    Retorna uma lista de strings, onde cada string representa
    uma Feature (com seus cenários).
    """

    features = []      # Lista final com todas as Features extraídas
    current_block = [] # Acumulador temporário para o bloco atual de comentários

    # Abrimos o arquivo no caminho especificado
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Caso a linha seja comentário (começa com "#")
            if stripped.startswith("#"):
                # Remove "#" e espaços extras, deixando apenas o conteúdo
                uncommented = stripped.lstrip("#").strip()

                if uncommented:  # só adiciona se a linha não for vazia
                    current_block.append(uncommented)

            else:
                # Se chegamos a uma linha normal e já estávamos montando um bloco
                if current_block:
                    # Junta todas as linhas do bloco em um único texto
                    features.append("\n".join(current_block))
                    current_block = []  # limpa para a próxima Feature

        # Se terminar o arquivo e ainda existir bloco pendente → salva
        if current_block:
            features.append("\n".join(current_block))

    return features
