# Multi-stage Dockerfile for TorBot
# Stage 1: Build stage
FROM python:3.11.4 as builder

# Set working directory
WORKDIR /build

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11.4-slim as runtime

# Create non-root user for security
RUN groupadd -r torbot && useradd -r -g torbot torbot

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=torbot:torbot . /app

# Set environment variables
ENV PYTHONPATH="/app"
ENV SOCKS5_PORT=9050
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER torbot

# Expose port
EXPOSE $SOCKS5_PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "torbot.py", "--help"]

# Labels for better image management
LABEL maintainer="TorBot Team"
LABEL version="4.2.0"
LABEL description="TorBot - A web scraping and analysis tool with Tor support"
