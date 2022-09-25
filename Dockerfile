FROM python:3.8-slim@sha256:d20122663d629b8b0848e2bb78d929c01aabab37c920990b37bb32bc47328818 as build
ENV POETRY_VERSION=1.2.1
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential gcc curl wget gnupg && \
    # Mongo
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt-get update -y && \ 
    apt-get install -y mongodb-org && \
    mkdir -p /data/db && \
    # Cleanup
    apt-get autoremove -y && \
    apt-get clean -y && \
    curl -sSL https://install.python-poetry.org | python -

WORKDIR /app
ENV PATH="/root/.local/bin:$PATH"
COPY pyproject.toml .
COPY poetry.lock .
RUN $HOME/.local/bin/poetry config virtualenvs.create true && \
    $HOME/.local/bin/poetry config virtualenvs.in-project true && \
    $HOME/.local/bin/poetry install --no-interaction --no-ansi --extras mongo

# ------------------------------------------------ test ------------------------------------------------
FROM build as test
COPY tasks.py tasks.py
COPY expert_dollup ./expert_dollup
RUN  poetry run invoke env:init --hostname 127.0.0.1 --username '' --password ''
COPY assets ./assets
COPY migrations ./migrations
COPY tests ./tests
CMD [ "bash", "-c", "(mongod > /dev/null &) && poetry run invoke db:migrate && poetry run pytest" ]

# ------------------------------------------------ staging ------------------------------------------------
FROM build as staged_venv
RUN $HOME/.local/bin/poetry install --only main --no-interaction --no-ansi --extras mongo

# ------------------------------------------------ migration ------------------------------------------------
FROM python:3.8-slim@sha256:d20122663d629b8b0848e2bb78d929c01aabab37c920990b37bb32bc47328818 as migration
WORKDIR /app
COPY --from=build /app/.venv ./venv
COPY migrations ./migrations
COPY tasks.py tasks.py
ENV PATH="/app/venv/bin:$PATH"
CMD [ "bash", "-c", "python -m invoke db:migrate" ]

# ------------------------------------------------ release ------------------------------------------------
FROM python:3.8-slim@sha256:d20122663d629b8b0848e2bb78d929c01aabab37c920990b37bb32bc47328818 as release
WORKDIR /app
RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python && \
    mkdir -p /app && chown python:python /app

USER python
COPY --chown=python:python --from=staged_venv /app/.venv ./venv
COPY --chown=python:python assets ./assets
COPY --chown=python:python expert_dollup ./expert_dollup

ENV FASTAPI_ENV=production
ENV DEBUG=false
ENV PORT=8000
ENV PATH="/app/venv/bin:$PATH"
CMD [ "python", "-m", "uvicorn", "--host", "0.0.0.0", "--port", "8000", "expert_dollup.main:app" ]
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 CMD curl -f https://127.0.0.1:8000/health

