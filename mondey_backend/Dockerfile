FROM python:3.14-slim

LABEL org.opencontainers.image.source=https://github.com/ssciwr/mondey-frontend-prototype
LABEL org.opencontainers.image.description="MONDEY backend production image"

COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /bin/

WORKDIR /app

# install the dependency versions from uv.lock (without the dev dependencies), using the python from the base image
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=never

# install the dependencies first, so this layer is cached if only the source code changes
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

COPY . .
RUN uv sync --locked --no-editable

ENV PATH="/app/.venv/bin:$PATH"

CMD ["/bin/sh", "-c", "alembic upgrade head && mondey-backend"]
