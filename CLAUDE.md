# CLAUDE.md - WhatsApp MCP Server Development Guide

## Project Overview

This is a **Model Context Protocol (MCP)** server that enables AI assistants (like Claude) to interact with WhatsApp. It consists of two main components that work together:

1. **Go WhatsApp Bridge** - Handles authentication and message synchronization with WhatsApp
2. **Python MCP Server** - Provides standardized tools for AI assistants to access WhatsApp data

**Key Capabilities:**
- Search and read personal WhatsApp messages (including media)
- Search contacts
- Send messages to individuals or groups
- Send media files (images, videos, documents, audio)
- Download media from messages
- Access message history with context

## Architecture

```
┌─────────────────┐
│  Claude/AI      │
│  Assistant      │
└────────┬────────┘
         │ MCP Protocol
         ▼
┌─────────────────────────┐
│ Python MCP Server       │
│ (whatsapp-mcp-server/)  │
│ - FastMCP framework     │
│ - Tool definitions      │
│ - API client            │
└────┬───────────────┬────┘
     │               │
     │ HTTP API      │ Direct SQLite
     │ (port 8080)   │ queries
     ▼               ▼
┌─────────────────────────┐
│ Go WhatsApp Bridge      │
│ (whatsapp-bridge/)      │
│ - WhatsApp connection   │
│ - Message sync          │
│ - SQLite storage        │
└─────────────────────────┘
         │
         │ whatsmeow library
         ▼
┌─────────────────────────┐
│ WhatsApp Web API        │
└─────────────────────────┘
```

## Directory Structure

```
whatsapp-mcp/
├── whatsapp-bridge/           # Go application
│   ├── main.go               # Main Go bridge server
│   ├── go.mod                # Go dependencies
│   ├── go.sum                # Go dependency checksums
│   └── store/                # SQLite databases (created at runtime)
│       ├── whatsapp.db       # WhatsApp session/device data
│       └── messages.db       # Message history
│
├── whatsapp-mcp-server/      # Python MCP server
│   ├── main.py               # MCP tool definitions and FastMCP setup
│   ├── whatsapp.py           # Core WhatsApp operations & database queries
│   ├── audio.py              # Audio file conversion (FFmpeg wrapper)
│   ├── pyproject.toml        # Python dependencies
│   └── uv.lock               # Locked dependencies
│
├── README.md                 # User-facing documentation
├── CLAUDE.md                 # This file - AI assistant guide
├── LICENSE
└── example-use.png
```

## Key Components

### 1. Go WhatsApp Bridge (`whatsapp-bridge/main.go`)

**Purpose:** Manages WhatsApp connection and message persistence

**Key Responsibilities:**
- QR code authentication via `whatsmeow` library
- Real-time message handling (`handleMessage`)
- History synchronization (`handleHistorySync`)
- SQLite database management (2 databases: session + messages)
- REST API server (port 8080) for send/download operations
- Media handling (upload/download)

**Important Functions:**
- `sendWhatsAppMessage()` - Send text/media messages
- `downloadMedia()` - Download media from messages
- `handleMessage()` - Process incoming real-time messages
- `handleHistorySync()` - Process historical message batches
- `GetChatName()` - Resolve chat names from JIDs
- `analyzeOggOpus()` - Parse Opus audio for voice messages

**Database Schema:**
```sql
-- messages.db
CREATE TABLE chats (
    jid TEXT PRIMARY KEY,
    name TEXT,
    last_message_time TIMESTAMP
);

CREATE TABLE messages (
    id TEXT,
    chat_jid TEXT,
    sender TEXT,
    content TEXT,
    timestamp TIMESTAMP,
    is_from_me BOOLEAN,
    media_type TEXT,
    filename TEXT,
    url TEXT,
    media_key BLOB,
    file_sha256 BLOB,
    file_enc_sha256 BLOB,
    file_length INTEGER,
    PRIMARY KEY (id, chat_jid),
    FOREIGN KEY (chat_jid) REFERENCES chats(jid)
);
```

### 2. Python MCP Server (`whatsapp-mcp-server/`)

**main.py** - MCP Tool Definitions
- Defines all MCP tools using FastMCP framework
- Acts as thin wrapper around `whatsapp.py` functions
- Handles tool parameter validation
- Returns structured responses to AI assistants

**whatsapp.py** - Core Business Logic
- Database queries and operations
- HTTP client for Go bridge API
- Message formatting and presentation
- Contact/chat search logic
- Media download coordination

**audio.py** - Audio Processing
- FFmpeg wrapper for audio conversion
- Converts audio files to Opus .ogg format
- Required for WhatsApp voice messages
- Handles temporary file management

**Key Data Classes:**
```python
@dataclass
class Message:
    timestamp: datetime
    sender: str
    content: str
    is_from_me: bool
    chat_jid: str
    id: str
    chat_name: Optional[str]
    media_type: Optional[str]

@dataclass
class Chat:
    jid: str
    name: Optional[str]
    last_message_time: Optional[datetime]
    last_message: Optional[str]
    last_sender: Optional[str]
    last_is_from_me: Optional[bool]

@dataclass
class Contact:
    phone_number: str
    name: Optional[str]
    jid: str
```

## Data Flow

### Reading Messages
1. AI assistant calls MCP tool (e.g., `list_messages`)
2. `main.py` receives request and calls `whatsapp.list_messages()`
3. `whatsapp.py` queries `messages.db` directly via SQLite
4. Results formatted and returned through MCP to assistant

### Sending Messages
1. AI assistant calls `send_message` or `send_file` tool
2. `main.py` calls `whatsapp.send_message()` or `whatsapp.send_file()`
3. `whatsapp.py` makes HTTP POST to `http://localhost:8080/api/send`
4. Go bridge validates recipient, uploads media if needed
5. Go bridge sends via WhatsApp Web API
6. Success/failure response returned through chain

### Media Download
1. AI assistant calls `download_media` with message_id and chat_jid
2. `whatsapp.py` makes HTTP POST to `http://localhost:8080/api/download`
3. Go bridge queries database for media metadata
4. Go bridge downloads from WhatsApp servers using `whatsmeow`
5. Media saved to `store/{chat_jid}/{filename}`
6. Absolute file path returned to assistant

## Development Workflows

### Setting Up Development Environment

```bash
# Terminal 1: Start Go bridge
cd whatsapp-bridge
go run main.go
# Scan QR code on first run

# Terminal 2: Test MCP server
cd whatsapp-mcp-server
uv run main.py
# Or install and run via MCP client (Claude Desktop)
```

### Testing Changes

**Go Bridge:**
```bash
cd whatsapp-bridge
go build && ./whatsapp-client
# Check for compilation errors
# Monitor console output for message handling
```

**Python Server:**
```bash
cd whatsapp-mcp-server
# Test direct Python execution
uv run main.py

# Or test through Claude Desktop
# Check Claude Desktop logs:
# macOS: ~/Library/Logs/Claude/mcp*.log
```

### Database Inspection

```bash
# View messages database
sqlite3 whatsapp-bridge/store/messages.db
> SELECT * FROM chats LIMIT 10;
> SELECT * FROM messages WHERE chat_jid = 'SOME_JID' ORDER BY timestamp DESC LIMIT 20;
> .schema messages

# View session database
sqlite3 whatsapp-bridge/store/whatsapp.db
> .tables
```

### Debugging Tips

1. **Connection Issues:**
   - Check if Go bridge is running on port 8080
   - Verify WhatsApp connection: look for "Connected to WhatsApp" log
   - Check QR code scan if newly authenticated

2. **Message Not Appearing:**
   - Wait for history sync to complete (can take minutes)
   - Check Go bridge console for "History sync complete" message
   - Query database directly to verify messages are stored

3. **Media Download Failures:**
   - Verify media metadata exists in database
   - Check file permissions in `store/` directory
   - Ensure WhatsApp session is active

4. **Audio Conversion Errors:**
   - Verify FFmpeg is installed: `ffmpeg -version`
   - Check audio file format is supported
   - Fallback: use `send_file` instead of `send_audio_message`

## Code Conventions

### Go Code (`whatsapp-bridge/`)

- **Error Handling:** Always return errors, log warnings/errors appropriately
- **Database Operations:** Use prepared statements, always close connections
- **Logging:** Use `logger.Infof/Warnf/Errorf` from waLog
- **API Responses:** Return JSON with `success` boolean and `message` string
- **Media Types:** Use `whatsmeow.MediaType` constants (MediaImage, MediaVideo, MediaAudio, MediaDocument)

### Python Code (`whatsapp-mcp-server/`)

- **Type Hints:** Always use type hints for function parameters and returns
- **Dataclasses:** Use dataclasses for structured data (Message, Chat, Contact)
- **Error Handling:** Return empty lists/None on errors, print errors for debugging
- **Database:** Use context managers (`with` statements) for connections (actually not used, but should be)
- **API Calls:** Use requests library, handle HTTP errors gracefully
- **Tool Definitions:** Use FastMCP's `@mcp.tool()` decorator with clear docstrings

### Naming Conventions

**JID (Jabber ID):** WhatsApp's unique identifier format
- Individual: `{phone_number}@s.whatsapp.net`
- Group: `{group_id}@g.us`
- Always use full JID for database operations

**Phone Numbers:**
- Store without `+` or other symbols
- Include country code
- Example: `12025551234` not `+1-202-555-1234`

**Media Types:**
- `image`, `video`, `audio`, `document` (lowercase, singular)

## Common Tasks for AI Assistants

### Adding a New MCP Tool

1. **Define function in `whatsapp.py`:**
```python
def get_user_status(jid: str) -> Optional[str]:
    """Get WhatsApp status/about for a user."""
    # Implementation
    pass
```

2. **Add tool wrapper in `main.py`:**
```python
@mcp.tool()
def get_user_status(jid: str) -> Dict[str, Any]:
    """Get WhatsApp status message for a contact.

    Args:
        jid: The contact's JID
    """
    status = whatsapp_get_user_status(jid)
    return {"jid": jid, "status": status}
```

3. **Test the tool** through Claude Desktop

### Adding Go Bridge API Endpoint

1. **Add handler in `main.go`:**
```go
http.HandleFunc("/api/status", func(w http.ResponseWriter, r *http.Request) {
    // Parse request
    var req StatusRequest
    json.NewDecoder(r.Body).Decode(&req)

    // Process
    status := getWhatsAppStatus(client, req.JID)

    // Respond
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(StatusResponse{
        Success: true,
        Status: status,
    })
})
```

2. **Add Python client function in `whatsapp.py`:**
```python
def get_user_status(jid: str) -> Optional[str]:
    response = requests.post(
        f"{WHATSAPP_API_BASE_URL}/status",
        json={"jid": jid}
    )
    if response.status_code == 200:
        return response.json().get("status")
    return None
```

### Modifying Database Schema

1. **Update schema in `main.go` `NewMessageStore()`:**
```go
_, err = db.Exec(`
    ALTER TABLE messages ADD COLUMN new_field TEXT;
`)
```

2. **Update queries in both Go and Python** to include new field

3. **Consider migration:** For production, handle existing databases gracefully

### Troubleshooting Message Sync Issues

**Check these in order:**

1. **Go bridge logs:** Is history sync being received?
```
History sync complete. Stored N messages.
```

2. **Database content:**
```sql
SELECT COUNT(*) FROM messages;
SELECT COUNT(*) FROM chats;
```

3. **WhatsApp connection:**
```
✓ Connected to WhatsApp!
```

4. **MCP tool execution:** Test with a known chat
```python
list_chats(limit=5)  # Should return recent chats
```

## Security & Privacy Considerations

⚠️ **Important Security Notes:**

1. **Local Data Storage:** All messages stored in SQLite databases in `store/`
2. **No Cloud Sync:** Data never leaves local machine except through AI assistant access
3. **Project Injection Risk:** MCP servers are vulnerable to prompt injection attacks
4. **Sensitive Files:** Never commit `store/` directory (contains session + messages)
5. **API Access:** Go bridge API (port 8080) has no authentication - local use only

## Dependencies

### Go Dependencies (whatsapp-bridge)
- `go.mau.fi/whatsmeow` - WhatsApp Web API library
- `github.com/mattn/go-sqlite3` - SQLite driver (requires CGO)
- `github.com/mdp/qrterminal` - QR code display
- `google.golang.org/protobuf` - Protocol buffers

### Python Dependencies (whatsapp-mcp-server)
- `mcp[cli]>=1.6.0` - Model Context Protocol framework
- `requests>=2.32.3` - HTTP client for Go bridge API
- `httpx>=0.28.1` - Alternative HTTP client

### External Dependencies
- **Go** - Required for whatsapp-bridge
- **Python 3.11+** - Required for MCP server
- **UV** - Python package manager
- **FFmpeg** - Optional, for audio conversion

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `CGO_ENABLED=0` | SQLite driver needs CGO | Set `CGO_ENABLED=1` and install C compiler |
| `Failed to connect to database` | Database file locked/missing | Check file permissions, close other connections |
| `Not connected to WhatsApp` | WhatsApp session expired | Re-scan QR code |
| `HTTP 500` from API | Go bridge error | Check Go bridge logs |
| `Failed to download media` | Media no longer available | Media expired on WhatsApp servers |
| `Error converting file to opus ogg` | FFmpeg not installed | Install FFmpeg or use `send_file` |

## File References

### Critical Files
- `whatsapp-bridge/main.go:789-923` - Main application loop
- `whatsapp-bridge/main.go:206-372` - Message sending logic
- `whatsapp-bridge/main.go:1009-1148` - History sync handler
- `whatsapp-mcp-server/main.py:1-251` - All MCP tool definitions
- `whatsapp-mcp-server/whatsapp.py:124-223` - Message listing with context
- `whatsapp-mcp-server/whatsapp.py:625-651` - Send message implementation

### Configuration Files
- `whatsapp-bridge/go.mod` - Go dependencies
- `whatsapp-mcp-server/pyproject.toml` - Python dependencies
- `~/Library/Application Support/Claude/claude_desktop_config.json` - Claude Desktop MCP config

## Testing Checklist

When making changes, verify:

- [ ] Go bridge compiles without errors
- [ ] Python MCP server starts without errors
- [ ] Can authenticate with WhatsApp (QR code)
- [ ] Can list recent chats
- [ ] Can search messages
- [ ] Can send text message
- [ ] Can send image/media file
- [ ] Can download media from message
- [ ] Database updates correctly
- [ ] Error messages are clear and actionable

## Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [whatsmeow Library](https://github.com/tulir/whatsmeow)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

**Last Updated:** 2025-11-14
**For Questions:** Check README.md or create a GitHub issue
