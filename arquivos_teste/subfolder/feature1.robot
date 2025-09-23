*** Settings ***
Documentation     Testes de Login

*** Test Cases ***
Teste de Login Válido
    [Documentation]    Deve logar corretamente
    Log    Executando teste de login válido

# Feature: Login do usuário
#   Scenario: Login válido
#       Given o usuário está na tela de login
#       When ele preenche usuário e senha corretos
#       Then o sistema exibe a tela inicial
#
#   Scenario: Login inválido
#       Given o usuário está na tela de login
#       When ele preenche usuário ou senha incorretos
#       Then o sistema exibe uma mensagem de erro
