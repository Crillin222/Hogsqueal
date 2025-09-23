*** Settings ***
Documentation     Testes de Carrinho

*** Test Cases ***
Adicionar Produto
    Log    Adicionando produto no carrinho

# Feature: Carrinho de Compras
#   Scenario: Adicionar produto
#       Given o usuário está na página do produto
#       When ele clica em "Adicionar ao carrinho"
#       Then o produto aparece no carrinho
#
#   Scenario: Remover produto
#       Given o carrinho tem produtos
#       When o usuário remove um produto
#       Then o carrinho fica vazio
