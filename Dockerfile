FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/
COPY server_config.json ./

# Install dependencies using uv
RUN uv sync --no-dev

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/config

# Set Python path
ENV PYTHONPATH=/app/src

# Create entrypoint script
RUN echo '#!/bin/bash\n\
if [ "$1" = "chat" ] || [ "$1" = "interactive" ] || [ "$1" = "cmd" ]; then\n\
    exec uv run mcp-cli "$@"\n\
elif [ "$1" = "shell" ]; then\n\
    exec /bin/bash\n\
else\n\
    exec uv run mcp-cli chat --server sqlite "$@"\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port for any web interfaces
EXPOSE 8000

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--help"]