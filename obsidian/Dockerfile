FROM oven/bun:1-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Supergateway still needs Node.js
RUN apt-get update && apt-get install -y curl &&     curl -fsSL https://deb.nodesource.com/setup_20.x | bash - &&     apt-get install -y nodejs

RUN npm install -g supergateway

# Clone and Build with Bun
RUN git clone https://github.com/jacksteamdev/obsidian-mcp-tools.git /tmp/repo
WORKDIR /tmp/repo

# Install all workspace dependencies
RUN bun install

# Build the server
WORKDIR /tmp/repo/packages/mcp-server
RUN bun run build

# Set the binary path
ENV BIN_PATH="/tmp/repo/packages/mcp-server/dist/mcp-server"
RUN chmod +x $BIN_PATH

# Entrypoint: Use REST API mode (no --vault-path)
CMD ["sh", "-c", "npx supergateway --port 8080 --stdio \"$BIN_PATH\""]
