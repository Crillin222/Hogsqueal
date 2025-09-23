Feature: Pagamento
Scenario: Pagamento aprovado
Given o usuário está no checkout
When ele paga com cartão válido
Then a compra é concluída com sucesso

Scenario: Pagamento recusado
Given o usuário está no checkout
When ele paga com cartão inválido
Then o sistema informa erro no pagamento

Feature: Carrinho de Compras
Scenario: Adicionar produto
Given o usuário está na página do produto
When ele clica em "Adicionar ao carrinho"
Then o produto aparece no carrinho

Scenario: Remover produto
Given o carrinho tem produtos
When o usuário remove um produto
Then o carrinho fica vazio