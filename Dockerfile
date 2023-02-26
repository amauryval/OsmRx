ARG PYTHON_VERS=3.11.0-slim

### BUILD REQUIREMENTS.txt ###
FROM python:$PYTHON_VERS as requirements

RUN python -m pip install --no-cache-dir --upgrade poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export --without dev -f requirements.txt --without-hashes -o requirements.txt

### INSTALL REQUIREMENTS ###
FROM python:$PYTHON_VERS AS installation

COPY --from=requirements requirements.txt .

RUN python -m venv /opt/venv
# to use the virtual env
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

### BUILD APP ###
FROM python:$PYTHON_VERS AS app_back

COPY --from=installation /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

# Switching to non-root user
RUN useradd ava
USER ava

CMD ["/bin/bash", "-c"]
