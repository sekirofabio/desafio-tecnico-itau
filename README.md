# Backend - Desafio Tecnico Itau

API desenvolvida em FastAPI com integracao a OpenAI e persistencia em PostgreSQL.

## Stack principal

- Python 3.12
- FastAPI
- SQLAlchemy
- LangChain
- PostgreSQL

## Pre-requisitos

- Docker e Docker Compose
- Chave de API da OpenAI

## Como executar

### 1) Clonar o repositorio

```bash
git clone git@github.com:sekirofabio/desafio-tecnico-itau.git

cd desafio-tecnico-itau/backend
```

### 2) Criar o arquivo .env

Crie um arquivo `.env` na raiz do projeto (mesmo nivel do `docker-compose.yml`) com a variavel:

```bash
OPENAI_API_KEY=<Chave API da OpenAI>
```

### Variaveis de ambiente

Obrigatorias:

- `OPENAI_API_KEY`: chave de API da OpenAI usada para gerar os resumos.

Opcionais (ja definidas no `docker-compose.yml`, util para ajustes locais):

- `POSTGRES_USER` (padrao: `postgres`)
- `POSTGRES_PASSWORD` (padrao: `postgres`)
- `POSTGRES_DB` (padrao: `app`)
- `POSTGRES_HOST` (padrao: `db`)

### 3) Subir a aplicacao

```bash
docker compose up --build -d
```

### 4) Verificar saude da API

```bash
curl http://localhost:8000/health
```

## Documentacao da API

- Swagger: http://localhost:8000/docs/

## Exemplos de uso

### Gerar um resumo

```bash
curl "http://localhost:8000/summarize?word=Steve%20Jobs&word_count=140"
```

### Listar termos com resumos salvos

```bash
curl "http://localhost:8000/summary/database"
```

### Buscar resumos salvos por termo

```bash
curl "http://localhost:8000/summary/database/Steve%20Jobs"
```

## Fluxo de dados

- O endpoint `/summarize` busca o artigo na Wikipedia, gera o resumo com a OpenAI e salva artigo + resumo no PostgreSQL.
- O endpoint `/summary/database` lista todos os resumos salvos no banco.
- O endpoint `/summary/database/{word}` filtra os resumos salvos por termo.

## Exemplos de resposta

### Healthcheck

```json
{"status":"ok"}
```

### /summarize

```json
{"word":"Steve Jobs","url":"https://pt.wikipedia.org/wiki/Steve_Jobs","summary":"..."}
```

### /summary/database

```json
{"summaries":[{"word":"Steve Jobs","word_count":140,"created_at":"2024-01-01T12:00:00"}]}
```

### /summary/database/{word}

```json
{"summaries":[{"word":"Steve Jobs","word_count":140,"summary":"...","created_at":"2024-01-01T12:00:00"}]}
```

## Testes

### Unitarios

```bash
docker compose exec api pytest
```

### Integracao

```bash
docker compose run --rm \
  -e RUN_INTEGRATION=1 \
  -e OPENAI_API_KEY=<Chave API da OpenAI> \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=app \
  -e POSTGRES_HOST=db \
  api pytest -k integration
```

## Troubleshooting

- Porta 8000 em uso: altere o mapeamento em `docker-compose.yml` ou libere a porta.
- Erro de conexao com o banco: aguarde o container `db` iniciar e tente novamente.
- Erro de autenticacao OpenAI: confirme se `OPENAI_API_KEY` esta correta no `.env`.
