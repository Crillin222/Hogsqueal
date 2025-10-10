Feature: Testes automatizados gerados pela aplicação Hobgoblin

@oiee @teste
Scenario: Pagamento aprovado
Given o usuário está no checkout
When ele paga com cartão válido
Then a compra é concluída com sucesso

@oiee @teste
Scenario: Pagamento recusado
Given o usuário está no checkout
When ele paga com cartão inválido
Then o sistema informa erro no pagamento

@oiee @teste
Scenario: Adicionar produto
Given o usuário está na página do produto
When ele clica em "Adicionar ao carrinho"
Then o produto aparece no carrinho

@oiee @teste
Scenario: Remover produto
Given o carrinho tem produtos
When o usuário remove um produto
Then o carrinho fica vazio

@oiee @teste
Scenario: Login válido
Given o usuário está na tela de login
When ele preenche usuário e senha corretos
Then o sistema exibe a tela inicial

@oiee @teste
Scenario: Login inválido
Given o usuário está na tela de login
When ele preenche usuário ou senha incorretos
Then o sistema exibe uma mensagem de erro