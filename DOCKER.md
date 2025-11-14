# 🐳 WhatsApp MCP - Guia Docker Completo

Documentação completa para executar o WhatsApp MCP usando Docker com toda a infraestrutura otimizada.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Início Rápido](#início-rápido)
- [Comandos Disponíveis](#comandos-disponíveis)
- [Arquitetura Docker](#arquitetura-docker)
- [Configuração Avançada](#configuração-avançada)
- [Troubleshooting](#troubleshooting)
- [Manutenção](#manutenção)

---

## 🎯 Visão Geral

A stack Docker do WhatsApp MCP inclui:

- **WhatsApp Bridge** (Go) - Porta 8080
  - Multi-stage build otimizado
  - Usuário não-root
  - Health checks configurados
  - Imagem Alpine minimal (~15MB)

- **Backend API** (Python FastAPI) - Porta 8000
  - Virtual environment isolado
  - Integração com Claude AI e MCP
  - Logging estruturado
  - Auto-restart em falhas

- **Frontend Web** (Next.js) - Porta 3000
  - Build standalone otimizado
  - SSR com cache
  - Modo production
  - Asset optimization

**Recursos:**
- ✅ Health checks automáticos
- ✅ Restart policies inteligentes
- ✅ Resource limits configurados
- ✅ Logs rotacionados
- ✅ Volumes persistentes
- ✅ Rede isolada
- ✅ Dependências ordenadas

---

## 📦 Pré-requisitos

### Obrigatórios

```bash
# Docker Engine
docker --version
# Docker version 24.0.0 ou superior

# Docker Compose
docker-compose --version
# Docker Compose version v2.20.0 ou superior
```

### Opcional (para desenvolvimento)

- Make (para usar Makefile)
- Git (para atualizações)
- curl (para health checks manuais)

### Chave da API

Você precisará de uma chave da API da Anthropic:
- Crie uma conta em: https://console.anthropic.com/
- Gere sua API key
- Tenha a key em mãos para configuração

---

## 🚀 Início Rápido

### Método 1: Script Automático (Recomendado)

```bash
# 1. Clone o repositório (se ainda não fez)
git clone <repo-url>
cd whatsapp-mcp

# 2. Execute o script de início
./start.sh
```

O script irá:
1. ✓ Verificar pré-requisitos
2. ✓ Criar .env se necessário
3. ✓ Pedir sua API key
4. ✓ Criar diretórios necessários
5. ✓ Build das imagens Docker
6. ✓ Iniciar todos os serviços
7. ✓ Exibir instruções de uso

### Método 2: Makefile

```bash
# Ver todos os comandos disponíveis
make help

# Iniciar serviços
make start

# Ver status
make status

# Ver logs
make logs
```

### Método 3: Docker Compose Manual

```bash
# 1. Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Adicione sua ANTHROPIC_API_KEY

# 2. Build e start
docker-compose up --build -d

# 3. Ver logs
docker-compose logs -f
```

### Primeiro Acesso

1. Abra o navegador em: **http://localhost:3000**
2. Aguarde o QR code aparecer (pode levar 30-60 segundos)
3. Abra WhatsApp no celular
4. Vá em: **Configurações → Aparelhos conectados → Conectar aparelho**
5. Escaneie o QR code exibido
6. Aguarde conexão ser estabelecida
7. Comece a conversar!

---

## 🎮 Comandos Disponíveis

### Scripts Bash

| Script | Descrição |
|--------|-----------|
| `./start.sh` | Inicia todos os serviços com checks |
| `./stop.sh` | Para todos os serviços |
| `./logs.sh` | Visualiza logs interativamente |
| `./status.sh` | Mostra status detalhado dos serviços |

### Makefile

| Comando | Descrição |
|---------|-----------|
| `make help` | Mostra todos os comandos |
| `make start` | Inicia serviços |
| `make stop` | Para serviços |
| `make restart` | Reinicia serviços |
| `make logs` | Visualiza logs |
| `make status` | Status dos serviços |
| `make build` | Build sem cache |
| `make rebuild` | Rebuild e restart |
| `make clean` | Remove tudo (dados inclusos) |
| `make ps` | Lista containers |
| `make health` | Verifica saúde dos serviços |

### Logs Específicos

```bash
# Via Makefile
make logs-bridge    # Go bridge
make logs-backend   # Python backend
make logs-frontend  # Next.js frontend

# Via Docker Compose
docker-compose logs -f whatsapp-bridge
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f  # Todos juntos
```

### Shell nos Containers

```bash
# Via Makefile
make shell-bridge
make shell-backend
make shell-frontend

# Via Docker
docker exec -it whatsapp-bridge sh
docker exec -it whatsapp-backend sh
docker exec -it whatsapp-frontend sh
```

---

## 🏗️ Arquitetura Docker

### Diagrama de Containers

```
┌─────────────────────────────────────────────┐
│          whatsapp-mcp-network               │
│              (172.28.0.0/16)                │
│                                             │
│  ┌──────────────────┐                       │
│  │  frontend:3000   │◄──┐                   │
│  │  (Next.js)       │   │                   │
│  └──────────────────┘   │                   │
│           │              │                   │
│           ▼              │ health checks     │
│  ┌──────────────────┐   │ & depends_on      │
│  │  backend:8000    │◄──┤                   │
│  │  (FastAPI)       │   │                   │
│  └──────────────────┘   │                   │
│           │              │                   │
│           ▼              │                   │
│  ┌──────────────────┐   │                   │
│  │  bridge:8080     │◄──┘                   │
│  │  (Go)            │                       │
│  └──────────────────┘                       │
│           │                                 │
└───────────┼─────────────────────────────────┘
            │
            ▼
     whatsapp-data
     (volume persistente)
```

### Health Checks

Todos os serviços possuem health checks configurados:

**WhatsApp Bridge:**
```yaml
CMD: curl -f http://localhost:8080/api/connection-status
Interval: 30s
Timeout: 10s
Start Period: 40s
Retries: 3
```

**Backend:**
```yaml
CMD: curl -f http://localhost:8000/
Interval: 30s
Timeout: 10s
Start Period: 20s
Retries: 3
```

**Frontend:**
```yaml
CMD: curl -f http://localhost:3000/
Interval: 30s
Timeout: 10s
Start Period: 30s
Retries: 3
```

### Resource Limits

Cada serviço tem limites de recursos definidos:

| Serviço | CPU Limit | Memory Limit | CPU Reserve | Memory Reserve |
|---------|-----------|--------------|-------------|----------------|
| Bridge  | 1.0       | 512M         | 0.25        | 256M           |
| Backend | 2.0       | 1G           | 0.5         | 512M           |
| Frontend| 1.0       | 512M         | 0.25        | 256M           |

### Volumes

```yaml
whatsapp-data:
  - Tipo: bind mount
  - Path: ./whatsapp-bridge/store
  - Persistência: Sessão WhatsApp + Mensagens
  - Size: ~100MB-1GB (depende do histórico)
```

### Networks

```yaml
whatsapp-mcp-network:
  - Driver: bridge
  - Subnet: 172.28.0.0/16
  - Isolation: Container-to-container
```

---

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

#### .env Principal

```bash
# API Key do Claude (OBRIGATÓRIO)
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# Modelo do Claude (Opcional)
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Timezone (Opcional)
TZ=America/Sao_Paulo
```

#### Variáveis do Backend

Você pode sobrescrever no docker-compose.yml:

```yaml
environment:
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
  - ANTHROPIC_MODEL=claude-sonnet-4-20250514
  - WHATSAPP_BRIDGE_URL=http://whatsapp-bridge:8080
  - WHATSAPP_BRIDGE_WS_URL=ws://whatsapp-bridge:8080
  - MCP_SERVER_COMMAND=uv
  - MCP_SERVER_ARGS=["run", "main.py"]
```

#### Variáveis do Frontend

```yaml
environment:
  - NEXT_PUBLIC_API_URL=http://localhost:8000
  - NODE_ENV=production
  - NEXT_TELEMETRY_DISABLED=1
```

### Customizar Portas

Edite o `docker-compose.yml`:

```yaml
services:
  whatsapp-bridge:
    ports:
      - "9080:8080"  # Mude 8080 para 9080

  backend:
    ports:
      - "9000:8000"  # Mude 8000 para 9000

  frontend:
    ports:
      - "4000:3000"  # Mude 3000 para 4000
```

Depois atualize as URLs no backend e frontend.

### Build com Cache

```bash
# Build rápido (usa cache)
docker-compose build

# Build sem cache (limpo)
docker-compose build --no-cache

# Build paralelo (mais rápido)
docker-compose build --parallel
```

### Modo de Desenvolvimento

Para desenvolvimento com hot-reload, você pode montar volumes:

```yaml
# docker-compose.dev.yml
services:
  backend:
    volumes:
      - ./whatsapp-web-backend/app:/app/app
    command: uvicorn app.main:app --reload --host 0.0.0.0

  frontend:
    volumes:
      - ./whatsapp-web-ui:/app
      - /app/node_modules
    command: npm run dev
```

Uso:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Serviço não inicia

```bash
# Ver logs detalhados
docker-compose logs <service-name>

# Verificar status
docker-compose ps

# Verificar health
docker inspect --format='{{.State.Health.Status}}' <container-name>
```

#### 2. QR Code não aparece

```bash
# Verificar logs do bridge
docker-compose logs -f whatsapp-bridge

# Verificar se a porta está acessível
curl http://localhost:8080/api/qrcode

# Restart do bridge
docker-compose restart whatsapp-bridge
```

#### 3. Backend não conecta ao MCP

```bash
# Verificar se MCP server está montado
docker exec -it whatsapp-backend ls /app/whatsapp-mcp-server

# Verificar logs
docker-compose logs -f backend

# Restart
docker-compose restart backend
```

#### 4. Erro de memória

```bash
# Verificar uso de recursos
docker stats

# Aumentar limites no docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

#### 5. Porta já em uso

```bash
# Encontrar processo usando a porta
lsof -i :3000
# ou
netstat -tulpn | grep 3000

# Matar processo ou mudar porta no docker-compose.yml
```

### Comandos de Debug

```bash
# Inspecionar container
docker inspect whatsapp-bridge

# Ver processos dentro do container
docker top whatsapp-bridge

# Estatísticas em tempo real
docker stats whatsapp-bridge whatsapp-backend whatsapp-frontend

# Verificar rede
docker network inspect whatsapp-mcp-network

# Verificar volumes
docker volume inspect whatsapp-mcp-data

# Health check manual
curl -f http://localhost:8080/api/connection-status
curl -f http://localhost:8000/
curl -f http://localhost:3000/
```

### Logs Estruturados

Os logs são salvos em JSON com rotação automática:

```bash
# Localização dos logs
/var/lib/docker/containers/<container-id>/<container-id>-json.log

# Configuração (já definida no docker-compose.yml)
logging:
  driver: "json-file"
  options:
    max-size: "10m"  # Máximo 10MB por arquivo
    max-file: "3"    # Mantém 3 arquivos
```

---

## 🔧 Manutenção

### Atualizações

```bash
# Método 1: Via Makefile
make update

# Método 2: Manual
git pull
docker-compose down
docker-compose up --build -d
```

### Backup

#### Backup dos Dados

```bash
# Backup do volume
docker run --rm \
  -v whatsapp-mcp-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/whatsapp-backup-$(date +%Y%m%d).tar.gz /data

# Ou simplesmente copie a pasta
cp -r whatsapp-bridge/store whatsapp-backup-$(date +%Y%m%d)
```

#### Restaurar Backup

```bash
# Restaurar do tar.gz
docker run --rm \
  -v whatsapp-mcp-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/whatsapp-backup-YYYYMMDD.tar.gz -C /

# Ou copie de volta
cp -r whatsapp-backup-YYYYMMDD whatsapp-bridge/store
```

### Limpeza

```bash
# Parar e remover containers (mantém dados)
docker-compose down

# Remover tudo incluindo volumes
docker-compose down -v

# Limpar imagens não usadas
docker image prune -a

# Limpar tudo do Docker
docker system prune -a --volumes
```

### Monitoramento

#### Com Docker Stats

```bash
# Tempo real
docker stats

# Com formatação
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

#### Com Logs

```bash
# Seguir logs de todos os serviços
docker-compose logs -f

# Filtrar por nível de log
docker-compose logs | grep ERROR
docker-compose logs | grep WARNING
```

### Performance

#### Otimizar Imagens

As imagens já estão otimizadas com multi-stage builds, mas você pode:

```bash
# Ver tamanho das imagens
docker images | grep whatsapp-mcp

# Limpar build cache
docker builder prune

# Rebuild do zero
docker-compose build --no-cache
```

#### Otimizar Volumes

```bash
# Verificar tamanho do volume
du -sh whatsapp-bridge/store

# Limpar logs antigos no volume
docker exec whatsapp-bridge sh -c "find /app/store -name '*.log' -mtime +7 -delete"
```

---

## 📊 Melhores Práticas

### Segurança

1. **Nunca commite .env com chaves reais**
   ```bash
   # Adicione ao .gitignore
   .env
   .env.local
   ```

2. **Use secrets para produção**
   ```yaml
   # docker-compose.prod.yml
   secrets:
     anthropic_key:
       external: true
   ```

3. **Mantenha usuários não-root**
   - Já configurado em todos os Dockerfiles

4. **Atualize regularmente**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

### Performance

1. **Use BuildKit para builds mais rápidos**
   ```bash
   DOCKER_BUILDKIT=1 docker-compose build
   ```

2. **Build paralelo**
   ```bash
   docker-compose build --parallel
   ```

3. **Limite recursos adequadamente**
   - Já configurado no docker-compose.yml

### Monitoramento

1. **Configure alertas para health checks**
2. **Monitore uso de recursos**
3. **Faça backups regulares**
4. **Mantenha logs organizados**

---

## 🆘 Suporte

### Logs Importantes

Quando reportar problemas, inclua:

```bash
# Status dos serviços
docker-compose ps

# Logs de todos os serviços
docker-compose logs --tail=100

# Health status
docker inspect --format='{{.State.Health}}' whatsapp-bridge
docker inspect --format='{{.State.Health}}' whatsapp-backend
docker inspect --format='{{.State.Health}}' whatsapp-frontend

# Recursos
docker stats --no-stream
```

### Informações do Sistema

```bash
docker version
docker-compose version
uname -a
free -h
df -h
```

---

## 📚 Recursos Adicionais

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [WhatsApp MCP Documentation](./WEB_README.md)
- [CLAUDE.md](./CLAUDE.md) - Documentação técnica detalhada

---

**Desenvolvido com ❤️ usando Docker e Claude AI**
