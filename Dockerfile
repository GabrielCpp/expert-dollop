FROM python:3.8-slim as build

ENV POETRY_VERSION=1.1.12

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc curl
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

WORKDIR /usr/app
COPY pyproject.toml .
COPY poetry.lock .

RUN $HOME/.poetry/bin/poetry config virtualenvs.create true && \
    $HOME/.poetry/bin/poetry config virtualenvs.in-project true && \
    $HOME/.poetry/bin/poetry install --no-dev --no-interaction --no-ansi --extras postgres

FROM python:3.8-slim@sha256:d20122663d629b8b0848e2bb78d929c01aabab37c920990b37bb32bc47328818

ENV FASTAPI_ENV=production
ENV DEBUG=false

RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python && \
    mkdir /usr/app && chown python:python /usr/app

USER python
WORKDIR /usr/app

COPY --chown=python:python --from=build /usr/app/.venv ./venv
COPY --chown=python:python expert_dollup ./expert_dollup

RUN python3 -m venv /usr/app/venv
ENV PATH="/usr/app/venv/bin:$PATH"

CMD [ "python", "-m", "uvicorn", "--host", "0.0.0.0:5000", "expert_dollup.main:app" ]
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f https://localhost:5000/health

