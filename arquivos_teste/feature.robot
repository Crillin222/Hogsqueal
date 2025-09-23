*** Settings ***
Documentation     Testes de Pagamento

*** Test Cases ***
Pagamento com Cartão
    Log    Pagamento via cartão de crédito

# Feature: Pagamento
#   Scenario: Pagamento aprovado
#       Given o usuário está no checkout
#       When ele paga com cartão válido
#       Then a compra é concluída com sucesso
#
#   Scenario: Pagamento recusado
#       Given o usuário está no checkout
#       When ele paga com cartão inválido
#       Then o sistema informa erro no pagamento
