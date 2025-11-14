# WhatsApp MCP Web Interface

Uma interface web completa para interagir com o WhatsApp através de um assistente AI powered by Claude, usando Model Context Protocol (MCP).

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Go](https://img.shields.io/badge/Go-1.24-00ADD8?logo=go)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi)

## 🎯 Visão Geral

Este projeto estende o WhatsApp MCP Server original com uma interface web completa que permite:

1. **Escanear QR Code via navegador** - Interface visual para autenticação do WhatsApp
2. **Chat com AI estilo Claude.ai** - Interface de conversação moderna e intuitiva
3. **Acesso total ao MCP** - O assistente AI pode buscar e enviar mensagens do WhatsApp
4. **Arquitetura de microserviços** - Componentes independentes e escaláveis

## 🏗️ Arquitetura

```
┌─────────────────────┐
│   Frontend Web      │ (Next.js + React)
│   Port: 3000        │
│   - QR Scanner UI   │
│   - Chat Interface  │
└──────────┬──────────┘
           │ HTTP + WebSocket
           ▼
┌─────────────────────────┐
│   Backend API           │ (Python FastAPI)
│   Port: 8000            │
│   - Claude API Client   │
│   - MCP Client          │
│   - WebSocket Server    │
└────┬────────────┬───────┘
     │            │
     │ HTTP       │ JSON-RPC
     ▼            ▼
┌──────────┐   ┌────────────────┐
│ Go Bridge│   │ MCP Server     │
│ Port:8080│   │ (Python)       │
│ WhatsApp │   │ - MCP Tools    │
│ Connection│   │ - DB Access    │
└──────────┘   └────────────────┘
     │
     │ whatsmeow
     ▼
┌──────────────┐
│ WhatsApp API │
└──────────────┘
```

## 📦 Componentes

### 1. WhatsApp Bridge (Go) - `whatsapp-bridge/`
- **Porta:** 8080
- **Função:** Gerencia conexão com WhatsApp
- **Novos Endpoints:**
  - `GET /api/qrcode` - Retorna QR code em base64
  - `GET /api/connection-status` - Status da conexão
  - `WS /ws/status` - WebSocket para updates em tempo real

### 2. Backend Web (Python FastAPI) - `whatsapp-web-backend/`
- **Porta:** 8000
- **Função:** Orquestra comunicação entre frontend, Claude API e MCP
- **Endpoints:**
  - `GET /api/qrcode` - Proxy para Go bridge
  - `GET /api/connection-status` - Status de conexão
  - `POST /api/chat` - Enviar mensagem para Claude
  - `WS /ws/whatsapp-status` - Status updates do WhatsApp
  - `WS /ws/chat` - Chat streaming

### 3. Frontend Web (Next.js) - `whatsapp-web-ui/`
- **Porta:** 3000
- **Função:** Interface de usuário
- **Componentes:**
  - `QRCodeScanner` - Exibe QR code e monitora status
  - `ChatInterface` - Interface de chat estilo Claude.ai

## 🚀 Início Rápido

### Pré-requisitos

- **Docker & Docker Compose** (recomendado) OU
- Go 1.24+
- Python 3.11+
- Node.js 20+
- Anthropic API Key

### Opção 1: Docker Compose (Recomendado)

1. **Clone o repositório e configure as variáveis:**

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env e adicione sua API key
nano .env
# Adicione: ANTHROPIC_API_KEY=sua_chave_aqui
```

2. **Inicie todos os serviços:**

```bash
docker-compose up --build
```

3. **Acesse a interface:**

Abra seu navegador em: http://localhost:3000

4. **Escaneie o QR code** com seu WhatsApp

5. **Comece a conversar!**

### Opção 2: Executar Manualmente

#### Passo 1: WhatsApp Bridge (Go)

```bash
cd whatsapp-bridge
go mod tidy
CGO_ENABLED=1 go build -o whatsapp-bridge main.go
./whatsapp-bridge
```

#### Passo 2: MCP Server (Python)

```bash
cd whatsapp-mcp-server
uv pip install -e .
# O MCP server será iniciado automaticamente pelo backend
```

#### Passo 3: Backend Web (Python)

```bash
cd whatsapp-web-backend

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env e adicione ANTHROPIC_API_KEY

# Instale dependências
pip install uv
uv pip install -r pyproject.toml

# Inicie o servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Passo 4: Frontend (Next.js)

```bash
cd whatsapp-web-ui

# Configure variáveis de ambiente
cp .env.local.example .env.local

# Instale dependências
npm install

# Inicie em modo desenvolvimento
npm run dev
```

#### Acesse: http://localhost:3000

## 🔧 Configuração

### Backend (.env)

```env
# Anthropic API Key (obrigatório)
ANTHROPIC_API_KEY=sua_chave_aqui

# Claude Model (opcional)
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# WhatsApp Bridge URLs (opcional)
WHATSAPP_BRIDGE_URL=http://localhost:8080
WHATSAPP_BRIDGE_WS_URL=ws://localhost:8080

# MCP Server (opcional)
MCP_SERVER_COMMAND=uv
MCP_SERVER_ARGS=["run", "main.py"]
MCP_SERVER_CWD=../whatsapp-mcp-server
```

### Frontend (.env.local)

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📱 Como Usar

### 1. Primeira Vez - Autenticação

1. Acesse http://localhost:3000
2. Aguarde o QR code aparecer
3. Abra WhatsApp no celular
4. Vá em **Configurações** → **Aparelhos conectados**
5. Toque em **Conectar um aparelho**
6. Escaneie o QR code exibido na tela
7. Aguarde a conexão ser estabelecida

### 2. Usando o Chat

Após conectado, você verá a interface de chat. Exemplos de uso:

**Buscar mensagens:**
```
"Mostre minhas últimas mensagens"
"O que João disse ontem?"
"Buscar mensagens sobre 'reunião'"
```

**Ver contatos:**
```
"Liste meus contatos"
"Buscar contato Maria"
```

**Enviar mensagens:**
```
"Envie 'Olá' para João"
"Mande uma mensagem para o grupo Família"
```

**Acessar histórico:**
```
"Mostre o histórico do chat com Maria"
"Últimas 10 mensagens do grupo Trabalho"
```

## 🎨 Interface

### QR Code Scanner
- Design moderno e responsivo
- Animações de loading
- Instruções claras de uso
- Feedback visual de status

### Chat Interface
- Estilo similar ao Claude.ai
- Mensagens em tempo real
- Indicador de digitação
- Histórico de conversação
- Sugestões de perguntas
- Timestamps
- Auto-scroll

## 🔒 Segurança

⚠️ **IMPORTANTE:**

1. **API Keys:** Nunca comite arquivos `.env` com chaves reais
2. **Acesso Local:** Por padrão, a aplicação não tem autenticação - use apenas localmente
3. **Dados Sensíveis:** Mensagens são armazenadas localmente em `store/messages.db`
4. **Prompt Injection:** MCP servers são vulneráveis a prompt injection - use com cuidado
5. **CORS:** Configurado para desenvolvimento - ajuste para produção

## 🐛 Troubleshooting

### QR Code não aparece

```bash
# Verifique se o Go bridge está rodando
curl http://localhost:8080/api/qrcode

# Verifique logs
docker-compose logs whatsapp-bridge
```

### Backend não conecta ao MCP

```bash
# Verifique se o MCP server está acessível
cd whatsapp-mcp-server
uv run main.py

# Verifique logs do backend
docker-compose logs backend
```

### Frontend não carrega

```bash
# Verifique se o backend está rodando
curl http://localhost:8000/

# Verifique variáveis de ambiente
cat whatsapp-web-ui/.env.local

# Reconstrua o frontend
cd whatsapp-web-ui
rm -rf .next node_modules
npm install
npm run dev
```

### Mensagens não aparecem

```bash
# Verifique o banco de dados
sqlite3 whatsapp-bridge/store/messages.db
> SELECT COUNT(*) FROM messages;

# Aguarde a sincronização do histórico (pode demorar alguns minutos)
```

## 🏗️ Desenvolvimento

### Estrutura de Arquivos

```
whatsapp-mcp/
├── whatsapp-bridge/          # Go WhatsApp Bridge
│   ├── main.go               # Código principal
│   ├── go.mod                # Dependências Go
│   ├── Dockerfile            # Docker image
│   └── store/                # Dados persistentes
│
├── whatsapp-web-backend/     # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── claude_client.py  # Cliente Claude
│   │   ├── mcp_client.py     # Cliente MCP
│   │   ├── models.py         # Modelos Pydantic
│   │   └── config.py         # Configurações
│   ├── pyproject.toml        # Dependências Python
│   └── Dockerfile            # Docker image
│
├── whatsapp-web-ui/          # Next.js Frontend
│   ├── app/
│   │   ├── page.tsx          # Página principal
│   │   ├── layout.tsx        # Layout
│   │   └── globals.css       # Estilos globais
│   ├── components/
│   │   ├── QRCodeScanner.tsx # Scanner QR
│   │   └── ChatInterface.tsx # Interface chat
│   ├── lib/
│   │   └── api.ts            # Cliente API
│   ├── package.json          # Dependências Node
│   └── Dockerfile            # Docker image
│
├── whatsapp-mcp-server/      # MCP Server original
│   ├── main.py               # Ferramentas MCP
│   └── whatsapp.py           # Lógica WhatsApp
│
├── docker-compose.yml        # Orquestração
├── .env.example              # Variáveis exemplo
└── WEB_README.md             # Esta documentação
```

### Adicionando Novas Funcionalidades

#### 1. Nova Ferramenta MCP

Adicione em `whatsapp-mcp-server/main.py`:

```python
@mcp.tool()
def nova_ferramenta(parametro: str) -> Dict[str, Any]:
    """Descrição da ferramenta"""
    # Implementação
    return {"resultado": "sucesso"}
```

#### 2. Novo Endpoint Backend

Adicione em `whatsapp-web-backend/app/main.py`:

```python
@app.get("/api/novo-endpoint")
async def novo_endpoint():
    return {"status": "ok"}
```

#### 3. Novo Componente Frontend

Crie em `whatsapp-web-ui/components/NovoComponente.tsx`:

```typescript
export default function NovoComponente() {
  return <div>Novo Componente</div>
}
```

## 📝 Tecnologias Utilizadas

- **Backend Go:** whatsmeow, gorilla/websocket, skip2/go-qrcode
- **Backend Python:** FastAPI, Anthropic SDK, websockets
- **Frontend:** Next.js 15, React 19, TailwindCSS, TypeScript
- **MCP:** FastMCP framework
- **Database:** SQLite
- **Container:** Docker, Docker Compose

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto mantém a mesma licença do projeto original.

## 🙏 Créditos

Construído sobre o [WhatsApp MCP Server](../README.md) original.

- **whatsmeow:** https://github.com/tulir/whatsmeow
- **FastMCP:** https://github.com/jlowin/fastmcp
- **Anthropic Claude:** https://www.anthropic.com

## 📞 Suporte

Para questões e suporte:
- Veja o [README original](../README.md) para detalhes do MCP Server
- Consulte [CLAUDE.md](../CLAUDE.md) para documentação técnica
- Abra uma issue no GitHub

---

**Desenvolvido com ❤️ usando Claude AI**
