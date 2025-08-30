# Docker Setup Guide for MCP CLI

This guide explains how to run MCP CLI using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB available disk space (for Ollama models)

## Quick Start

### 1. Basic Setup

Clone the repository and start the services:

```bash
git clone <repository-url>
cd mcp-cli
cp .env.example .env  # Edit with your API keys if needed
docker-compose up -d
```

### 2. Run MCP CLI in Chat Mode

```bash
# Interactive chat mode
docker-compose run --rm mcp-cli chat --server sqlite

# Or start interactive container
docker-compose run --rm -it mcp-cli shell
```

### 3. Wait for Ollama Model Download

The first startup will download the default `gpt-oss` model (~4GB). Monitor progress:

```bash
# Check Ollama logs
docker-compose logs -f ollama

# Check if model is ready
docker-compose exec ollama ollama list
```

## Service Architecture

The Docker setup includes these services:

### Core Services

- **mcp-cli**: Main application container
- **ollama**: Local LLM inference server with gpt-oss model
- **sqlite-server**: MCP SQLite server with sample database

### Optional Services (Profiles)

- **filesystem-server**: MCP filesystem server (`--profile filesystem`)
- **brave-search-server**: Web search server (`--profile search`)
- **portainer**: Container management UI (`--profile monitoring`)

## Usage Examples

### Basic Chat Mode

```bash
# Start with default services
docker-compose up -d

# Run chat mode
docker-compose run --rm mcp-cli chat --server sqlite

# Run with different model
docker-compose run --rm mcp-cli chat --server sqlite --model llama3.3
```

### Interactive Mode

```bash
# Start interactive shell
docker-compose run --rm mcp-cli interactive --server sqlite

# Or get a bash shell in the container
docker-compose run --rm mcp-cli shell
```

### Command Mode

```bash
# List tools
docker-compose run --rm mcp-cli tools --server sqlite

# Execute specific tool
docker-compose run --rm mcp-cli cmd --server sqlite --tool list_tables

# Process files
echo "SELECT * FROM users" | docker-compose run --rm -i mcp-cli cmd --server sqlite --tool read_query --input -
```

### With Additional Services

```bash
# Start with filesystem server
docker-compose --profile filesystem up -d

# Start with search capabilities
docker-compose --profile search up -d

# Start with monitoring
docker-compose --profile monitoring up -d

# Access Portainer at http://localhost:9000
```

## Configuration

### Environment Variables

Copy and customize `.env.example` to `.env`:

```bash
cp .env.example .env
```

Key variables:
- `LLM_PROVIDER`: Default provider (ollama, openai, anthropic)
- `LLM_MODEL`: Default model (gpt-oss for ollama)
- `OPENAI_API_KEY`: For GPT-5, GPT-4 models
- `ANTHROPIC_API_KEY`: For Claude 4 models
- `MCP_TOOL_TIMEOUT`: Tool execution timeout

### Server Configuration

Edit `server_config.json` to configure MCP servers:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "python",
      "args": ["-m", "mcp_server.sqlite_server"],
      "env": {
        "DATABASE_PATH": "/app/database.db"
      }
    }
  }
}
```

### Volume Mounts

Default volume mounts:
- `./server_config.json` → `/app/server_config.json`
- `./logs` → `/app/logs`
- `./test.db` → `/app/database.db` (SQLite server)

## Development Mode

For development with live code editing:

```bash
# Start development services
docker-compose --profile development up -d

# Run with source code mounted
docker-compose run --rm mcp-cli-dev chat --server sqlite
```

Development features:
- Source code mounted for live editing
- Debug logging enabled
- Additional development models pre-loaded

## Cloud Providers

To use cloud providers instead of local Ollama:

### OpenAI (GPT-5, GPT-4, O3)

```bash
# Set API key in .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Run with OpenAI
docker-compose run --rm mcp-cli chat --server sqlite --provider openai --model gpt-5
```

### Anthropic (Claude 4)

```bash
# Set API key in .env
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env

# Run with Claude
docker-compose run --rm mcp-cli chat --server sqlite --provider anthropic --model claude-4-1-opus
```

### Multiple Providers

```bash
# Run interactive mode to switch providers
docker-compose run --rm mcp-cli interactive --server sqlite

# In interactive mode:
> provider openai gpt-5
> provider anthropic claude-4-sonnet
> provider ollama gpt-oss
```

## Troubleshooting

### Common Issues

**Ollama model not found:**
```bash
# Pull model manually
docker-compose exec ollama ollama pull gpt-oss
docker-compose exec ollama ollama pull llama3.3
```

**Permission issues:**
```bash
# Fix volume permissions
sudo chown -R $USER:$USER logs/ data/
chmod -R 755 logs/ data/
```

**Container not starting:**
```bash
# Check logs
docker-compose logs mcp-cli
docker-compose logs ollama

# Restart services
docker-compose restart
```

**Out of disk space:**
```bash
# Clean up Docker
docker system prune -f
docker volume prune -f

# Remove unused images
docker image prune -a -f
```

### Debugging

Enable debug logging:
```bash
# Set in .env
LOG_LEVEL=DEBUG

# Or run with debug flag
docker-compose run --rm mcp-cli chat --server sqlite --verbose --log-level DEBUG
```

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mcp-cli
docker-compose logs -f ollama
```

## Performance Optimization

### Ollama Performance

```bash
# Check GPU support
docker-compose exec ollama nvidia-smi

# For GPU acceleration, add to docker-compose.yml:
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Resource Limits

Add to services in docker-compose.yml:
```yaml
services:
  mcp-cli:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

## Security Considerations

- API keys are stored in `.env` file (not committed to git)
- Database files are mounted read-only where possible
- Network isolation via custom Docker network
- Non-root users in containers where feasible

## Production Deployment

For production use:

1. Use specific image tags instead of `latest`
2. Enable health checks and restart policies
3. Use Docker secrets for API keys
4. Configure proper logging and monitoring
5. Use external databases instead of local SQLite
6. Enable TLS termination at reverse proxy level

Example production overrides:
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  mcp-cli:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
  
  ollama:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
```

## Maintenance

### Regular Tasks

```bash
# Update images
docker-compose pull

# Clean up
docker system prune -f

# Backup data
docker-compose exec sqlite-server sqlite3 /app/database.db ".backup /app/data/backup.db"

# Update models
docker-compose exec ollama ollama pull gpt-oss
```

### Health Checks

```bash
# Check service health
docker-compose ps

# Test connectivity
docker-compose exec mcp-cli mcp-cli ping --server sqlite
docker-compose exec mcp-cli mcp-cli provider diagnostic
```