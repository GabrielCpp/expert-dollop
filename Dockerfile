FROM python:3.8-slim@sha256:d20122663d629b8b0848e2bb78d929c01aabab37c920990b37bb32bc47328818 as build
ENV POETRY_VERSION=1.1.12
WORKDIR /usr/app
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential gcc curl && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

COPY pyproject.toml .
COPY poetry.lock .
RUN $HOME/.poetry/bin/poetry config virtualenvs.create true && \
    $HOME/.poetry/bin/poetry config virtualenvs.in-project true && \
    $HOME/.poetry/bin/poetry install --no-dev --no-interaction --no-ansi --extras mongo

FROM build as test
WORKDIR /usr/app
ENV PATH="/root/.poetry/bin:$PATH"
RUN $HOME/.poetry/bin/poetry install --no-interaction --no-ansi --extras mongo

COPY tasks.py tasks.py
COPY assets ./assets
COPY migrations ./migrations
RUN poetry run invoke env:init --hostname mongo
COPY expert_dollup ./expert_dollup
COPY tests ./tests
CMD [ "poetry", "run", "pytest" ]

FROM python:3.8-slim@sha256:d20122663d629b8b0848e2bb78d929c01aabab37c920990b37bb32bc47328818 as release
RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python && \
    mkdir /usr/app && chown python:python /usr/app
USER python
WORKDIR /usr/app 
COPY --from=build /usr/app/.venv ./venv
COPY --chown=python:python assets ./assets
COPY --chown=python:python migrations ./migrations
COPY --chown=python:python expert_dollup ./expert_dollup

ENV FASTAPI_ENV=production
ENV DEBUG=false
ENV PATH="/usr/app/venv/bin:$PATH"
CMD [ "python", "-m", "uvicorn", "--host", "0.0.0.0:80", "expert_dollup.main:app" ]
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f https://localhost:80/health

