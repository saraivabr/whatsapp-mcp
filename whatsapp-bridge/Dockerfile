# ==============================================
# Build Stage - Compile Go application
# ==============================================
FROM golang:1.24-alpine AS builder

# Add metadata
LABEL stage=builder
LABEL description="Go WhatsApp Bridge Builder"

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    sqlite-dev \
    git

WORKDIR /build

# Copy dependency files first (better layer caching)
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download && go mod verify

# Copy source code
COPY main.go ./

# Build with optimizations
RUN CGO_ENABLED=1 GOOS=linux go build \
    -a \
    -installsuffix cgo \
    -ldflags="-w -s" \
    -o whatsapp-bridge .

# ==============================================
# Runtime Stage - Minimal production image
# ==============================================
FROM alpine:latest

# Add metadata
LABEL maintainer="WhatsApp MCP Project"
LABEL description="WhatsApp Bridge - WebSocket and REST API"
LABEL version="1.0.0"

# Install runtime dependencies
RUN apk add --no-cache \
    ca-certificates \
    sqlite-libs \
    tzdata \
    curl

# Create non-root user
RUN addgroup -g 1000 whatsapp && \
    adduser -D -u 1000 -G whatsapp whatsapp

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/whatsapp-bridge .

# Create store directory with correct permissions
RUN mkdir -p /app/store && \
    chown -R whatsapp:whatsapp /app

# Switch to non-root user
USER whatsapp

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/api/connection-status || exit 1

# Run the application
CMD ["./whatsapp-bridge"]
