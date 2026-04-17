# Studio Grade Backend (Optimized for Local Hive)
FROM python:3.12-bookworm
WORKDIR /app

# Point to local context and ensure uv is handled
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependencies first for caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Final environment prep
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8055

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8055"]
