@PBCTEST131
Feature: Pagamento
@3131
Scenario: Pagamento aprovado
Given o usuário está no checkout
When ele paga com cartão válido
Then a compra é concluída com sucesso

@3131
Scenario: Pagamento recusado
Given o usuário está no checkout
When ele paga com cartão inválido
Then o sistema informa erro no pagamento

@PBCTEST131
Feature: Carrinho de Compras
@3131
Scenario: Adicionar produto
Given o usuário está na página do produto
When ele clica em "Adicionar ao carrinho"
Then o produto aparece no carrinho

@3131
Scenario: Remover produto
Given o carrinho tem produtos
When o usuário remove um produto
Then o carrinho fica vazio

@PBCTEST131
Feature: Login do usuário
@3131
Scenario: Login válido
Given o usuário está na tela de login
When ele preenche usuário e senha corretos
Then o sistema exibe a tela inicial

@3131
Scenario: Login inválido
Given o usuário está na tela de login
When ele preenche usuário ou senha incorretos
Then o sistema exibe uma mensagem de erro