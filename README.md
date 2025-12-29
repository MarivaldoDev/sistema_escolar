# Sistema Escolar

Uma aplicação web para gerenciamento escolar (cadeias de ensino, turmas, disciplinas, notas, faltas e avisos) desenvolvida com Django. Este repositório contém a app principal `system`, templates e recursos estáticos, além de suporte a execução local via Django e via Docker (com Postgres no compose).

**Sumário**

- **Sobre**
- **Principais funcionalidades**
- **Estrutura do projeto**
- **Requisitos**
- **Executando localmente (Django)**
- **Executando com Docker (docker-compose)**
- **Testes**
- **Notas sobre static/media**

**Sobre**

Este projeto implementa um sistema escolar simples para gerenciar turmas, matérias, registros de presença, lançamentos de nota e avisos. Possui modelos personalizados de usuário, views para professores e alunos, templates e endpoints para operações comuns de um sistema escolar.

**Principais funcionalidades**

- Autenticação e perfis de usuário (professores e alunos)
- Gerenciamento de turmas e disciplinas
- Registro de presença (chamada)
- Lançamento e visualização de notas
- Avisos e lista de notificações
- Upload de imagens de cadastro e gerenciamento de mídia
- Painel administrativo (Django admin)

**Estrutura do projeto (pontos principais)**

- `manage.py` — utilitário de administração do Django
- `core/` — configuração do Django (settings, urls, wsgi, asgi)
- `system/` — app principal com modelos, views, templates e testes
- `base_static/` — arquivos estáticos (CSS, JS, imagens)
- `media/` — uploads de mídia (imagens de cadastro)
- `docker-compose.yml` e `Dockerfile` — configuração para execução em container
- `requirements.txt` — dependências Python

**Requisitos**

- Python 3.8+ (recomendado 3.10/3.11)
- pip
- Docker & Docker Compose (para execução com contêineres)

Executando localmente (Django)

1. Crie e ative um ambiente virtual:

```bash
Linux
    python3 -m venv venv
    source venv/bin/activate

Windows
    python -m venv venv
    .\venv\Scripts\activate
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Aplique migrações e crie um superusuário:

```bash
python manage.py migrate
python manage.py createsuperuser
```

4. Rode o servidor de desenvolvimento:

```bash
python manage.py runserver
```

5. Acesse a aplicação em `http://localhost:8000` e o admin em `http://localhost:8000/admin`.

Observação: por padrão o projeto usa SQLite quando não configurado para Postgres. O arquivo de banco local padrão é `db.sqlite3`.

Executando com Docker (docker-compose)

Este repositório já inclui um `docker-compose.yml` que define um serviço Postgres (`db`) e o serviço da aplicação chamado `sistema-escolar`.

1. Build e subir containers:

```bash
docker-compose build
docker-compose up -d
```

2. Executar migrações dentro do container da aplicação:

```bash
docker-compose exec sistema-escolar python manage.py migrate
docker-compose exec sistema-escolar python manage.py createsuperuser
```

3. Para ver logs em tempo real:

```bash
docker-compose logs -f
```

4. Para parar e remover containers:

```bash
docker-compose down
```

Variáveis de ambiente relevantes (definidas no `docker-compose.yml`):

- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

Testes

O projeto inclui testes com `pytest` em `system/tests/`.

Execute-os localmente (após instalar dependências):

```bash
pytest -q
```

Static e Media

- Arquivos estáticos estão em `base_static/` e são servidos automaticamente em desenvolvimento pelo `runserver`.
- Uploads de mídia são gravados em `media/`.

Boas práticas / Dicas

- Para produção, configure um servidor WSGI (Gunicorn/uwsgi), servi-los via um proxy (NGINX) e usar um storage adequado para `media` (S3, por exemplo).
- Configure variáveis sensíveis (SECRET_KEY, configurações de banco) via variáveis de ambiente ou um arquivo `.env` (não commitá-lo no repositório).

Contribuição

Contribuições são bem-vindas: abra issues ou pull requests com melhorias, correções de bugs ou novas funcionalidades.

Contato

Se precisar de ajuda com a configuração, execução ou ampliar o README, me avise.
