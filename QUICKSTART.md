# ⚡ WhatsApp MCP - Início Rápido

Guia rápido para colocar o WhatsApp MCP rodando em **5 minutos**!

## 🎯 O que é isso?

Uma **interface web completa** para conversar com seu WhatsApp usando **Claude AI**.

Você pode:
- 💬 Fazer perguntas sobre suas mensagens do WhatsApp
- 🔍 Buscar conversas antigas
- 📤 Enviar mensagens pelo chat
- 🤖 Usar IA para interagir com seus contatos
- 📱 Tudo via navegador!

## 🚀 Início Ultra-Rápido

### 1️⃣ Pré-requisitos

Você precisa apenas de:
- **Docker** instalado ([Download aqui](https://www.docker.com/get-started))
- **Chave da API Anthropic** ([Criar conta aqui](https://console.anthropic.com/))

### 2️⃣ Clonar e Configurar

```bash
# Clone o repositório
git clone <seu-repo-url>
cd whatsapp-mcp

# Execute o script de início
./start.sh
```

O script vai pedir sua **chave da API**. Cole ela quando solicitado.

### 3️⃣ Acessar e Escanear

1. Abra: **http://localhost:3000**
2. Escaneie o QR code com WhatsApp
3. Pronto! ✨

## 📋 Comandos Essenciais

```bash
# Iniciar tudo
./start.sh

# Ver logs
./logs.sh

# Status do sistema
./status.sh

# Parar tudo
./stop.sh
```

Ou use o **Makefile**:

```bash
make start    # Iniciar
make logs     # Ver logs
make status   # Status
make stop     # Parar
make help     # Ver todos os comandos
```

## 🎨 Interface

### Tela de QR Code
![QR Code Scanner](https://via.placeholder.com/800x400/4CAF50/FFFFFF?text=QR+Code+Scanner)

Escaneie com WhatsApp → Conecta automaticamente

### Tela de Chat
![Chat Interface](https://via.placeholder.com/800x400/2196F3/FFFFFF?text=Chat+Interface)

Interface estilo Claude.ai → Pergunte qualquer coisa sobre suas mensagens

## 💡 Exemplos de Uso

```
Você: Mostre minhas últimas mensagens
AI: Aqui estão suas últimas 10 mensagens...

Você: O que João disse ontem?
AI: João enviou 3 mensagens ontem...

Você: Envie "Oi" para Maria
AI: Mensagem enviada para Maria ✓

Você: Buscar mensagens sobre "reunião"
AI: Encontrei 5 mensagens sobre reunião...
```

## 🔧 Portas

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Go Bridge**: http://localhost:8080

## 📚 Mais Informações

- **Guia Completo**: [WEB_README.md](./WEB_README.md)
- **Docker Avançado**: [DOCKER.md](./DOCKER.md)
- **Documentação Técnica**: [CLAUDE.md](./CLAUDE.md)

## 🆘 Problemas?

### QR Code não aparece?
```bash
# Verificar logs
docker-compose logs -f whatsapp-bridge

# Reiniciar
docker-compose restart whatsapp-bridge
```

### Erro de API Key?
```bash
# Editar .env
nano .env
# Adicionar: ANTHROPIC_API_KEY=sua_chave_aqui

# Reiniciar
docker-compose restart backend
```

### Serviço não inicia?
```bash
# Ver status
docker-compose ps

# Ver logs de todos
docker-compose logs
```

## 🎉 Pronto!

Agora você tem:
✅ WhatsApp conectado via web
✅ AI assistant com acesso às mensagens
✅ Interface moderna e intuitiva
✅ Tudo rodando em Docker

**Divirta-se!** 🚀

---

**Precisa de ajuda?** Veja [WEB_README.md](./WEB_README.md) ou [DOCKER.md](./DOCKER.md)
