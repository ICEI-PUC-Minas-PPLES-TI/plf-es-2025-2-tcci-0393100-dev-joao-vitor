[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=20755406)

# DashVendas

> Plataforma de análise comercial que transforma dados de vendas em inteligência acionável, por meio de cálculo automatizado de KPIs, importação estruturada de planilhas, cruzamento inteligente de produtos e um assistente baseado em Inteligência Artificial.

Trabalho de Conclusão de Curso (TCC) em Engenharia de Software — PUC Minas.

- **Repositório:** https://github.com/ICEI-PUC-Minas-PPLES-TI/plf-es-2025-2-tcci-0393100-dev-joao-vitor

<p align="center">
  <img src="Artefatos/telas/dashboard.png" alt="Dashboard do DashVendas" width="80%">
</p>

---

## Índice

- [Sobre o projeto](#sobre-o-projeto)
- [Principais funcionalidades](#principais-funcionalidades)
- [Tecnologias utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e execução](#instalação-e-execução)
- [Configuração do ambiente (.env)](#configuração-do-ambiente-env)
- [Banco de dados](#banco-de-dados)
- [Credenciais de teste](#credenciais-de-teste)
- [Testes automatizados](#testes-automatizados)
- [Integração contínua (CI)](#integração-contínua-ci)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Imagens da aplicação](#imagens-da-aplicação)
- [Equipe e orientação](#equipe-e-orientação)
- [Licença](#licença)

---

## Sobre o projeto

O DashVendas é um sistema de apoio à decisão comercial. A partir de planilhas de vendas importadas pelo usuário, o sistema valida os dados, cruza os produtos informados com um catálogo interno (por código ou similaridade textual), consolida as informações e calcula indicadores de desempenho (KPIs) em tempo real. Sobre esses indicadores, o sistema acompanha metas, gera alertas automáticos de desempenho e oferece um assistente de IA capaz de interpretar os números e responder perguntas em linguagem natural.

O back-end concentra as regras de negócio e expõe uma API REST; o front-end é uma Single Page Application que consome essa API. A arquitetura segue uma organização em camadas (controllers → services → repositories → persistência), com aplicação de padrões de projeto (Strategy, Template Method, Adapter e Repository).

## Principais funcionalidades

- **Importação de planilhas Excel** em três etapas: importação, validação e cruzamento de produtos.
- **Validação automática** de dados, com detecção de campos ausentes, valores inválidos e registros duplicados.
- **Cruzamento de produtos** por código exato ou similaridade textual, com indicação de confiança.
- **Cálculo de KPIs em tempo real** (total de vendas, ticket médio, vendas por região e por categoria).
- **Gestão de metas** por período, região e categoria, com classificação de atingimento.
- **Alertas automáticos** de desempenho, gerados a partir das metas em risco ou não atingidas.
- **Relatórios gerenciais** consolidados e **agendamento** de envios periódicos.
- **Assistente de IA** para análise interpretativa e perguntas em linguagem natural (com modo local quando não há chave de API configurada).
- **Controle de acesso por perfil** (administrador, gestor, analista, vendedor e executivo).
- **Auditoria** das operações críticas por meio de logs.

## Tecnologias utilizadas

**Back-end**
- Python 3.11+
- FastAPI (framework web / API REST)
- SQLAlchemy (ORM)
- Pydantic (validação de dados)
- python-jose + passlib/bcrypt (autenticação JWT e hashing de senhas)
- pandas + openpyxl + xlrd (processamento de planilhas)
- SQLite (desenvolvimento) / PostgreSQL (produção, via psycopg2)
- pytest + httpx (testes automatizados)

**Front-end**
- React 18
- Vite
- React Router
- Axios

## Pré-requisitos

Antes de começar, garanta que possui instalado:

- [Python 3.11 ou superior](https://www.python.org/downloads/)
- [Node.js 18 ou superior](https://nodejs.org/) (inclui o npm)
- [Git](https://git-scm.com/)

## Instalação e execução

Clone o repositório:

```bash
git clone https://github.com/ICEI-PUC-Minas-PPLES-TI/plf-es-2025-2-tcci-0393100-dev-joao-vitor.git
cd plf-es-2025-2-tcci-0393100-dev-joao-vitor
```

### Back-end

Com o terminal aberto em `Codigo/BackEnd`:

```bash
# 1. Criar e ativar o ambiente virtual
py -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Configurar o arquivo .env (ver seção abaixo)

# 4. Iniciar a API (porta 8000)
uvicorn app.main:app --reload
```

A documentação interativa da API fica disponível em `http://localhost:8000/docs`.

### Front-end

Com o terminal aberto em `Codigo/Frontend`:

```bash
# 1. Instalar as dependências
npm install

# 2. Iniciar a aplicação (porta 5173)
npm run dev
```

Acesse `http://localhost:5173` no navegador.

## Configuração do ambiente (.env)

O back-end lê as configurações de um arquivo `.env` localizado em `Codigo/BackEnd`. Crie o arquivo com o seguinte conteúdo:

```env
# Chave da API da OpenAI (opcional).
# Se deixada em branco, o Assistente de IA opera em modo local.
OPENAI_API_KEY=

# String de conexão do banco de dados.
# Deixe em branco para usar SQLite local (padrão em desenvolvimento).
# Para PostgreSQL (ex.: Neon), informe a URL completa:
# DATABASE_URL=postgresql://usuario:senha@host/banco?sslmode=require
DATABASE_URL=
```

### Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | Não | Chave da API da OpenAI. Em branco, o assistente responde em modo local (sem chamadas externas). |
| `DATABASE_URL` | Não | String de conexão do banco. Em branco, usa SQLite local (`dashvendas.db`). Aceita PostgreSQL. |

> **Importante:** o arquivo `.env` está listado no `.gitignore` e não deve ser versionado, pois pode conter credenciais.

## Banco de dados

O sistema utiliza SQLAlchemy e funciona com dois bancos, sem alteração de código:

- **SQLite (desenvolvimento):** usado automaticamente quando `DATABASE_URL` está em branco. O arquivo `dashvendas.db` é criado na primeira execução.
- **PostgreSQL (produção):** basta informar a `DATABASE_URL` no `.env`.

Na primeira inicialização, o sistema cria as tabelas automaticamente e executa uma carga inicial (*seed*) com os usuários de acesso e as regiões de referência. **Não há necessidade de rodar migrações manualmente** — o esquema é criado a partir dos modelos na inicialização.

O catálogo de produtos e as vendas não fazem parte do *seed*: eles são carregados a partir dos dados reais, por meio da tela de importação.

## Credenciais de teste

Os usuários abaixo são criados automaticamente na primeira execução. A senha padrão de todos é `123456`.

| Perfil | E-mail | Senha |
|---|---|---|
| Administrador | `admin@dashvendas.com` | `123456` |
| Gestor comercial | `gestor@dashvendas.com` | `123456` |
| Analista de dados | `analista@dashvendas.com` | `123456` |
| Vendedor | `jose@dashvendas.com` | `123456` |
| Vendedora | `laisa@dashvendas.com` | `123456` |
| Executivo | `executivo@dashvendas.com` | `123456` |

> As senhas são apenas para demonstração e devem ser alteradas em ambiente real.

## Testes automatizados

Com o terminal aberto em `Codigo/BackEnd` (ambiente virtual ativado):

```bash
pytest
```

Para ver o detalhamento por caso de teste:

```bash
pytest -v
```

Os testes cobrem os serviços de negócio e as integrações internas entre componentes: cálculo de KPIs, importação, validação de planilhas, cruzamento de produtos, metas, alertas, usuários e o assistente de IA em modo local. Incluem ainda testes de autenticação e autorização (JWT e perfis de acesso), valores de fronteira, cenários negativos e resiliência a falhas de integração externa.

## Integração contínua (CI)

O repositório utiliza **GitHub Actions** para integração contínua. A cada `push` ou `pull request` nas branches principais, o workflow definido em [`.github/workflows/ci.yml`](.github/workflows/ci.yml) instala as dependências e executa toda a suíte de testes automaticamente, garantindo que novas alterações não quebrem funcionalidades existentes.

## Estrutura do repositório

```
.
├── .github/workflows/   # Integração contínua (GitHub Actions)
├── Artefatos/           # Diagramas, telas e vídeos das entregas
│   └── telas/           # Capturas de tela da aplicação
├── Codigo/
│   ├── BackEnd/         # API FastAPI
│   │   ├── app/
│   │   │   ├── controllers/   # Camada de entrada (rotas da API)
│   │   │   ├── services/      # Regras de negócio
│   │   │   ├── repositories/  # Acesso a dados
│   │   │   ├── db/            # Modelos, sessão e seed
│   │   │   ├── dtos/          # Objetos de transferência de dados
│   │   │   ├── integrations/  # Integração com serviços externos (IA)
│   │   │   └── core/          # Autenticação e utilidades
│   │   ├── tests/            # Testes automatizados (pytest)
│   │   └── requirements.txt
│   └── Frontend/        # Aplicação React + Vite
│       └── src/
│           ├── pages/        # Telas do sistema
│           ├── components/   # Componentes reutilizáveis
│           └── auth/         # Contexto de autenticação
├── Documentacao/        # Documento de Projeto, Visão e demais artefatos
├── Divulgacao/          # Material de divulgação
└── README.md
```

## Imagens da aplicação

### Autenticação e visão geral

<p align="center">
  <img src="Artefatos/telas/login.png" alt="Tela de Login" width="49%">
  <img src="Artefatos/telas/dashboard.png" alt="Dashboard" width="49%">
</p>

### Indicadores e desempenho individual

<p align="center">
  <img src="Artefatos/telas/indicadores.png" alt="Indicadores (KPIs)" width="49%">
  <img src="Artefatos/telas/MeuDesempenho.png" alt="Meu Desempenho (vendedor)" width="49%">
</p>

### Importação de planilhas (importação, validação e cruzamento)

<p align="center">
  <img src="Artefatos/telas/Importação.png" alt="Importação de planilha" width="32%">
  <img src="Artefatos/telas/Validação.png" alt="Validação dos dados" width="32%">
  <img src="Artefatos/telas/cruzamento.png" alt="Cruzamento de produtos" width="32%">
</p>

### Metas e alertas

<p align="center">
  <img src="Artefatos/telas/metas.png" alt="Metas" width="49%">
  <img src="Artefatos/telas/alertas.png" alt="Alertas" width="49%">
</p>

### Assistente de IA

<p align="center">
  <img src="Artefatos/telas/Ia.png" alt="Assistente de IA" width="80%">
</p>

### Relatórios, gestão de usuários e auditoria

<p align="center">
  <img src="Artefatos/telas/relatorios.png" alt="Relatórios" width="32%">
  <img src="Artefatos/telas/usuarios.png" alt="Gestão de usuários" width="32%">
  <img src="Artefatos/telas/logs.png" alt="Auditoria (logs)" width="32%">
</p>

## Equipe e orientação

**Aluno**
- João Vítor Rajão e Souza

**Orientador de TCC II**
- Marco Rodrigo Costa

**Professores de TCC I**
- Cleiton Silva Tavares
- Danilo de Quadros Maia Filho
- Leonardo Vilela Cardoso
- Raphael Ramos Dias Costa

## Licença

Este projeto está licenciado sob os termos indicados no arquivo [LICENSE](LICENSE).
