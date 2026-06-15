[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=20755406)
# DashVendas

O DashVendas é um sistema desenvolvido como Trabalho de Conclusão de Curso (TCC) em Engenharia de Software, com o objetivo de agilizar o processo de conferência de produtos presentes nos pedidos da empresa Polimetal, que muitas vezes chegam com códigos e nomenclaturas diferentes daqueles utilizados no sistema interno da organização. Essa divergência gera retrabalho e atraso na análise dos pedidos, impactando diretamente a eficiência das operações comerciais.

Entre os principais objetivos do projeto está a automação da relação entre pedidos recebidos e os produtos registrados no estoque, garantindo maior consistência na identificação, rastreabilidade e integração das informações. Além disso, o sistema disponibiliza dashboards interativos e relatórios inteligentes para gestores, vendedores e equipe administrativa, permitindo uma visão consolidada das vendas e facilitando a tomada de decisão estratégica.

## Alunos integrantes da equipe

* João Vítor Rajão e Souza


## Professores responsáveis

* Cleiton Silva Tavares
* Danilo de Quadros Maia Filho
* Leonardo Vilela Cardoso
* Raphael Ramos Dias Costa

## Orientador TCCII

*Marco Rodrigo Costa

## Instruções de utilização

### Configuração .env

* Adicionar o connection string e o token da OpenAI api

### Comandos para rodar o BackEnd

Com o terminal aberto em Codigo/BackEnd
* py -m venv .venv
* .venv\Scripts\activate
* pip install -r requirements.txt
* uvicorn app.main:app --reload

### Comandos para rodar o FrontEnd

Com o terminal aberto em Codigo/FrontEnd
* npm install
* npm run dev

### Comando rodar testes

Com o terminal aberto em Codigo/BackEnd

* pytest