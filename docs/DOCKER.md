# Docker Documentation for TorBot

This document provides comprehensive instructions for using TorBot with Docker.

## Overview

TorBot now uses a multi-stage Docker build for optimal performance and security. The build process creates a lightweight, secure container with non-root user execution.

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DedSecInside/TorBot.git
   cd TorBot
   ```

2. **Build and run:**
   ```bash
   docker-compose up torbot
   ```

3. **Run with custom parameters:**
   ```bash
   docker-compose run torbot -u https://example.onion --depth 3 --visualize tree
   ```

### Using Docker CLI

1. **Build the image:**
   ```bash
   docker build -t torbot:latest .
   ```

2. **Run basic scan:**
   ```bash
   docker run --rm torbot:latest -u https://example.com --depth 2
   ```

3. **Run with Tor proxy:**
   ```bash
   docker run --rm --network="host" torbot:latest -u https://example.onion --depth 2
   ```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SOCKS5_HOST` | SOCKS5 proxy host | `127.0.0.1` |
| `SOCKS5_PORT` | SOCKS5 proxy port | `9050` |

### Volume Mounts

Mount local directories for persistent data:

```bash
docker run --rm \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/logs:/app/logs \
  torbot:latest -u https://example.onion --save json
```

## Advanced Usage

### Custom Tor Configuration

Create a custom `docker-compose.yml` with Tor as a service:

```yaml
version: '3.8'
services:
  tor:
    image: dperson/torproxy:latest
    ports:
      - "9050:9050"
      - "9051:9051"
    environment:
      - PASSWORD=your_password
    restart: unless-stopped
    
  torbot:
    image: torbot:latest
    depends_on:
      - tor
    environment:
      - SOCKS5_HOST=tor
      - SOCKS5_PORT=9050
    volumes:
      - ./results:/app/results
    command: -u https://example.onion --depth 3 --visualize tree --save json
```

### Development Mode

For development with live code changes:

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  torbot-dev:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - .:/app
      - ./results:/app/results
    environment:
      - PYTHONPATH=/app
    command: python torbot.py --help
```

## Security Features

- **Non-root user**: Container runs as `torbot` user (UID 1000)
- **Minimal base image**: Uses `python:3.11.4-slim` for reduced attack surface
- **Layer caching**: Optimized Dockerfile for faster builds
- **Health checks**: Built-in container health monitoring

## Image Details

- **Base image**: `python:3.11.4-slim`
- **Final size**: ~200MB (optimized)
- **Python version**: 3.11.4
- **Working directory**: `/app`
- **Exposed ports**: 9050 (SOCKS5)

## Troubleshooting

### Common Issues

1. **Tor connection failed:**
   ```bash
   # Check if Tor is running on host
   netstat -tuln | grep 9050
   
   # Test with Docker
   docker run --rm --network="host" torbot:latest --help
   ```

2. **Permission denied:**
   Ensure Docker daemon is running and user has proper permissions.

3. **Build fails:**
   Check Docker version compatibility:
   ```bash
   docker --version  # Requires Docker 20.10+
   ```

### Debug Mode

Run with debug logging:
```bash
docker run --rm -e PYTHONPATH=/app torbot:latest -v -u https://example.com
```

## Performance Optimization

### Build Cache

Leverage Docker build cache:
```bash
# Build with cache
DOCKER_BUILDKIT=1 docker build -t torbot:latest .

# Build without cache (clean build)
docker build --no-cache -t torbot:latest .
```

### Resource Limits

Set resource constraints:
```bash
docker run --rm \
  --memory=512m \
  --cpus=1 \
  torbot:latest -u https://example.com --depth 2
```

## Contributing

When contributing Docker-related changes:

1. Test the build process: `docker build -t torbot:test .`
2. Verify functionality: `docker run --rm torbot:test --help`
3. Update this documentation if needed
4. Ensure `.dockerignore` excludes unnecessary files