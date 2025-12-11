# CloneBookLLM - Document Intelligence Application

A sophisticated web application that enables users to upload documents and ask intelligent questions about them. The application combines the Flask web framework with a local LLM + RAG/Agent system to provide document-specific and general knowledge responses. Cloud Gemini integration has been removed by default; local LLMs are recommended for private deployments.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [System Type](#system-type)
4. [Features](#features)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [How It Works](#how-it-works)
8. [API Endpoints](#api-endpoints)
9. [File Structure](#file-structure)
10. [Usage Guide](#usage-guide)
11. [Technical Details](#technical-details)
12. [Agent Tool-Use System](#agent-tool-use-system)
13. [Troubleshooting](#troubleshooting)

---

## Project Overview

CloneBookLLM is an intelligent document analysis system powered by **RAG + LangChain Agent** that:

- **Uploads & Processes Documents** - Accepts PDF, TXT, DOCX, PPT, and Markdown files
- **Semantic Search** - Uses vector embeddings for intelligent retrieval
- **Multi-Tool Agent** - Intelligently decides between document search, web search, and content generation
- **Smart Q&A System** - Answers questions based on document content or general knowledge
- **Hybrid Knowledge Base** - Provides document-specific answers and general advice
- **Real-time Chat UI** - Interactive chat interface for seamless conversation
- **Resource Extraction** - Automatically identifies and references resources in documents
- **Content Generation** - Generate PowerPoint presentations and audio files
- **Preview System** - View uploaded documents and generated outputs

### Use Cases

- Resume analysis and improvement suggestions
- Document summarization and Q&A
- Educational material review
- Technical documentation analysis
- Business document analysis
- Automated presentation generation
- Content-based audio creation

---

## Architecture

### Technology Stack

```
Frontend:
├── HTML (templates/index.html)
├── CSS (static/style.css)
└── JavaScript (static/script.js)

Backend:
├── Python 3.12
├── Flask 3.0.0 (Web Framework)
├── google-generativeai 0.7.0+ (Gemini API)
├── LangChain Framework (Agent & RAG)
│   ├── langchain
│   ├── langchain-google-genai
│   ├── langchain-huggingface
│   └── langchain-community
├── ChromaDB 0.4.10+ (Vector Store)
└── Document Processing (PyPDF2, python-docx)

AI/ML:
├── Google Gemini API (gemini-2.5-flash model)
├── HuggingFace Embeddings (all-MiniLM-L6-v2)
├── Vector Similarity Search (ChromaDB)
├── Web Search Tool (DuckDuckGo)
└── LangChain Agent (Multi-tool reasoning)

Storage:
├── Vector Store (Chroma - in-memory/persistent)
├── Document Store (Python dict - in-memory)
├── File Store (uploads/ folder)
└── Output Store (static/outputs/ folder)
```

---

## System Type

**Current Classification: Retrieval-Augmented Generation (RAG) + Agent System**

This system is a **hybrid approach combining**:

### 1. **RAG (Retrieval-Augmented Generation)**
- Vector embeddings for semantic search
- ChromaDB vector store for document chunks
- Top-k retrieval (default: 3 chunks)
- Reduced token usage vs full document passing

### 2. **Multi-Tool Agent (LangChain)**
- Structured reasoning with REACT loop
- 4 specialized tools:
  - 🔍 **Internal Document Search** - Semantic retrieval
  - 🌐 **Web Search** - DuckDuckGo integration
  - 📊 **PPT Generator** - Creates presentations
  - 🔊 **Audio Generator** - Text-to-speech

### 3. **Query Processing Strategy**

```
User Query
    │
    ├─ Tier 1: Agent with Tools (Primary)
    │   ├─ Agent analyzes query
    │   ├─ Selects appropriate tool
    │   │   ├─ Internal Docs? → Vector search
    │   │   ├─ Current events? → Web search
    │   │   ├─ Create PPT? → PPT tool
    │   │   └─ Audio? → Audio tool
    │   └─ Tool executes & returns result
    │
    └─ Tier 2: Fallback to Basic RAG (if agent fails)
        ├─ Semantic retrieval only
        ├─ Gemini for answer generation
        └─ Graceful degradation
```

### 4. **NOT an AI Agent if:**
- ❌ Uses only simple keyword search (this system uses semantic + agent)
- ❌ No tool selection capability (agent has 4 tools)
- ❌ No reasoning loop (agent uses REACT reasoning)

### 5. **IS a true Agent because:**
- ✅ Decides which tool to use based on query
- ✅ Performs multi-step reasoning
- ✅ Can chain tools (search → generate)
- ✅ Returns tool outputs with reasoning

---

```
┌─────────────────┐
│  User Browser   │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Upload │
    │ Document│
    └────┬────┘
         │
    ┌────▼──────────────┐
    │  Flask Backend    │
    │  (app.py)         │
    └────┬──────────────┘
         │
    ┌────▼──────────────────┐
    │  Document Processing  │
    │  - Extract Text       │
    │  - Store in Memory    │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────┐
    │  User Asks Question   │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────────┐
    │  Query Handler (/query)   │
    │  1. Check Document        │
    │  2. Extract Resources     │
    │  3. Ask Gemini (Doc-Based)│
    └────┬──────────────────────┘
         │
    ┌────▼──────────────┐
    │  Answer Found?    │
    └────┬────┬─────────┘
    YES │    │ NO
        │    │
    ┌───▼─┐ ┌─▼──────────────┐
    │Send │ │Get General     │
    │Answer   Advice from    │
    └───┬─┘ │Gemini (Hybrid) │
        │    └─┬──────────────┘
        │     │
        └─────┼──────────────┐
              │              │
        ┌─────▼──────────────▼──┐
        │  Return Response with  │
        │  - Answer              │
        │  - Source Type         │
        │  - Resources Found     │
        └─────┬──────────────────┘
              │
        ┌─────▼───────────┐
        │ Display in Chat │
        │ (Formatted)     │
        └─────────────────┘
```

---

## Agent Tool-Use System

### Overview

The agent system enables intelligent tool selection based on user queries. When a user asks a question, the agent analyzes it and decides which tool to use for the best answer.

### Tool Descriptions

#### 1. **Internal Document Search Tool**
**Triggered by:** Questions about uploaded document content

**Process:**
1. Agent recognizes query is about document
2. Performs semantic similarity search
3. Retrieves top-3 most relevant chunks
4. Generates answer from retrieved context
5. Returns with source citations

**Example Query:** "What are the main topics in this document?"

#### 2. **Web Search Tool**
**Triggered by:** Questions requiring current information not in documents

**Process:**
1. Agent detects query needs external knowledge
2. DuckDuckGo searches the web
3. Aggregates search results
4. Synthesizes answer from web data
5. Provides links to sources

**Example Query:** "What's the latest news about AI?"

#### 3. **PPT Generator Tool**
**Triggered by:** Requests to create presentations

**Process:**
1. Agent identifies presentation request
2. Extracts/summarizes relevant content
3. Structures slides with title + bullets
4. Generates PPTX file
5. Creates HTML preview
6. Returns file path

**Example Query:** "Create a presentation about this document" / "Make slides from chapter 3"

#### 4. **Audio Generator Tool**
**Triggered by:** Requests for audio/speech output

**Process:**
1. Agent recognizes audio request
2. Uses gTTS (Google Text-to-Speech)
3. Converts text to MP3
4. Stores in outputs folder
5. Returns audio file path

**Example Query:** "Create an audio summary" / "Convert this to speech"

### Agent Decision Logic

```
User Query
    │
    ├─ Parse Query Intent
    │   ├─ Contains "presentation/slides/ppt"?
    │   │   └─ YES → Use PPT Generator
    │   │
    │   ├─ Contains "audio/speech/convert"?
    │   │   └─ YES → Use Audio Generator
    │   │
    │   ├─ Contains "search/web/latest/news"?
    │   │   └─ YES → Use Web Search
    │   │
    │   └─ Default: Use Internal Document Search
    │       └─ Semantic search on uploaded docs
    │
    └─ Execute Selected Tool
        └─ Return Result
```

### Response Format from Agent

```json
{
  "success": true,
  "answer": "Agent response with tool output...",
  "query": "User's original query",
  "source_type": "agent",
  "retrieval_method": "agent_with_tools",
  "agent_used": true,
  "resources_found": ["https://..."],
  "rag_enabled": true
}
```

### Agent Configuration

In `agent.py`, the agent is configured with:

```python
agent = initialize_agent(
    tools=[Web Search, Internal Documents, PPT Generator, Audio Generator],
    llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash"),
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    memory=ConversationBufferMemory()
)
```

**Key Parameters:**
- **STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION** - Uses REACT reasoning with JSON parsing
- **verbose=True** - Logs agent reasoning steps
- **memory=ConversationBufferMemory()** - Maintains conversation context
- **handle_parsing_errors=True** - Graceful error handling

### Fallback Mechanism

If agent encounters an error:

```
Agent Fails
    │
    ├─ Log Error
    ├─ Print Warning
    │
    └─ Fallback to Basic RAG
        ├─ Retrieve top-3 chunks
        ├─ Pass to Gemini directly
        ├─ Generate answer
        └─ Return response with agent_used=false
```

### Performance Notes

- **Tool Selection:** ~0.2-0.5s
- **Vector Search:** ~0.1-0.3s
- **Gemini Response:** ~2-4s
- **Web Search:** ~1-3s
- **PPT Generation:** ~0.5-1s
- **Total Agent Query:** ~3-8s

---

### 1. **Document Upload & Processing**

- Supports multiple file formats: PDF, TXT, DOCX, MD
- Automatic text extraction from documents
- In-memory storage for quick access
- File validation and error handling

### 2. **Intelligent Q&A System**

- **Document-Specific Answers**: Directly from uploaded content
- **Hybrid Responses**: General knowledge when document doesn't cover topic
- **Resource Extraction**: Automatically identifies URLs and references
- **Context-Aware**: Distinguishes between document content and general advice

### 3. **Chat Interface**

- Real-time message display
- User and bot message differentiation
- Markdown formatting support:
  - `**bold**` for emphasis
  - `*italic*` for italics
  - Numbered and bulleted lists
- Auto-scrolling to latest messages
- Message persistence

### 4. **File Preview System**

- Preview uploaded PDFs, TXT, DOCX
- View generated output files
- Download functionality
- Supports audio playback for generated files

### 5. **Markdown Formatting**

The system supports rich text formatting in responses:

```
**Bold Text** → Rendered as <strong>
*Italic Text* → Rendered as <em>
1. Numbered → Proper list formatting
- Bullets → Indented bullet points
```

---

## Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager
- Google API Key (from Generative AI)

### Step 1: Clone/Setup Project

```bash
cd /home/batman/Projects/CloneBookLLM
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `langchain>=0.1.0` - Framework for agents & RAG
- `langchain-huggingface>=0.0.0` - HuggingFace embeddings
- `langchain-community>=0.0.0` - Community tools (DuckDuckGo, loaders)
- `chromadb>=0.4.10` - Vector database
- `sentence-transformers>=2.0.0` - Embedding model
- `transformers` / `accelerate` / `torch` - Optional: local model inference
- `Flask>=3.0.0` - Web framework
- `PyPDF2>=3.0.0` - PDF processing
- `python-docx>=0.8.0` - DOCX processing
- `gTTS>=2.4.0` - Text-to-speech

Note: Cloud Gemini dependencies were removed. To use a local LLM, set `USE_LOCAL_LLM=true` and `LOCAL_MODEL_NAME` in your `.env`.

### Step 4: Configure Environment

Create a `.env` file in the project root (example using a local HF model):

```
USE_LOCAL_LLM=true
LOCAL_MODEL_NAME=gpt2
HF_DEVICE=-1           # -1=CPU, 0..N = GPU device id
```

### Step 5: Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

---

## Configuration

### Environment Variables

```env
USE_LOCAL_LLM        # Optional: true/1 to enable local HF model usage
LOCAL_MODEL_NAME     # Optional: HF model id/path (default: gpt2)
HF_DEVICE            # Optional: device id for HF pipeline (-1=CPU)
FLASK_ENV            # Optional: development or production
DEBUG                # Optional: True for debug mode
```

### Application Configuration (in app.py)

```python
UPLOAD_FOLDER = 'uploads'              # Where files are stored
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'md'}
MAX_FILE_SIZE = 50 * 1024 * 1024      # 50MB limit
```

---

## How It Works

### Process Flow Overview

#### **Flow 1: User Uploads a Document**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER UPLOADS DOCUMENT                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Step 1: Select  │
                    │  File(s) & Click │
                    │     "Upload"     │
                    └──────────┬───────┘
                              │
                    ┌─────────▼──────────┐
                    │  Step 2: Frontend  │
                    │  Collects Files    │
                    │  (script.js:       │
                    │   uploadFiles())   │
                    └─────────┬──────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │  Multiple Files?                  │
            └────┬──────────────────────┬───────┘
                 │ YES (Array)          │ NO (Single)
                 │                      │
        ┌────────▼─────────┐   ┌────────▼────────┐
        │ FormData with    │   │ FormData with   │
        │ files[] key      │   │ file key        │
        └────────┬─────────┘   └────────┬────────┘
                 │                      │
                 └──────────┬───────────┘
                            │
                  ┌─────────▼──────────┐
                  │  Step 3: POST to   │
                  │  /upload endpoint  │
                  │  (Backend)         │
                  └─────────┬──────────┘
                            │
                  ┌─────────▼──────────────────┐
                  │  Step 4: Backend           │
                  │  Receives Request          │
                  │  (app.py: upload_file())   │
                  └─────────┬──────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │  Validation & Processing              │
        └─────────┬─────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬──────────────┐
    │             │             │              │
    ▼             ▼             ▼              ▼
┌────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
│Check   │  │Validate  │  │Extract  │  │Generate  │
│Files   │  │File Type │  │Text     │  │Doc ID    │
│Exist   │  │& Size    │  │Based on │  │(Filename)│
│        │  │          │  │Format   │  │          │
└───┬────┘  └────┬─────┘  └────┬────┘  └────┬─────┘
    │            │             │             │
    └────────────┴─────────────┴─────────────┘
                    │
        ┌───────────▼───────────┐
        │  Step 5: Text         │
        │  Extraction Switch    │
        └───────────┬───────────┘
        │
        ├─ PDF?  → PyPDF2.PdfReader()
        ├─ DOCX? → python-docx Document()
        ├─ TXT?  → Plain read()
        └─ MD?   → Plain read()
        │
        ▼
    ┌─────────────────┐
    │  Extract Text   │
    │  Content from   │
    │  Document       │
    └────────┬────────┘
             │
    ┌────────▼──────────────┐
    │  Step 6: Store in     │
    │  Memory (document_    │
    │  store dictionary)    │
    │  {                    │
    │    "filename": {...}, │
    │    "content": "...",  │
    │    "upload_time": .., │
    │    "size": ...        │
    │  }                    │
    └────────┬──────────────┘
             │
    ┌────────▼──────────────┐
    │  Step 7: Send         │
    │  Success Response to  │
    │  Frontend             │
    │  {                    │
    │    "success": true,   │
    │    "filename": "...", │
    │    "size": ...,       │
    │    "doc_id": "..."    │
    │  }                    │
    └────────┬──────────────┘
             │
    ┌────────▼──────────────┐
    │  Step 8: Frontend     │
    │  Displays Success     │
    │  Message & File in    │
    │  File List            │
    └────────┬──────────────┘
             │
    ┌────────▼──────────────┐
    │  USER CAN NOW:        │
    │  ✓ Ask Questions      │
    │  ✓ Preview Document   │
    │  ✓ Upload More Files  │
    └───────────────────────┘
```

**Key Points:**
- Files validated before processing
- Text extraction format-specific
- Document stored in memory for quick access
- Response sent immediately to frontend
- User can now interact with document

---

#### **Flow 2: User Asks a Question**

```
┌──────────────────────────────────────────────────────────────┐
│                    USER ASKS QUESTION                        │
└──────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼────────┐
                    │  Step 1: User    │
                    │  Types Question  │
                    │  in Chat Box &   │
                    │  Presses Enter   │
                    └─────────┬────────┘
                              │
                    ┌─────────▼──────────────┐
                    │  Step 2: Frontend      │
                    │  Validates Query       │
                    │  (sendQuery function   │
                    │   in script.js)        │
                    └─────────┬──────────────┘
                              │
                    ┌─────────▼──────────────┐
                    │  Step 3: Add User      │
                    │  Message to Chat UI    │
                    │  (addMessage(query,    │
                    │   'user'))             │
                    └─────────┬──────────────┘
                              │
                    ┌─────────▼──────────────┐
                    │  Step 4: Show          │
                    │  "Thinking..." Bot     │
                    │  Message              │
                    └─────────┬──────────────┘
                              │
                    ┌─────────▼──────────────┐
                    │  Step 5: POST Request  │
                    │  to /query Endpoint    │
                    │  JSON Payload:         │
                    │  {                     │
                    │    "query": "How to    │
                    │    improve?"           │
                    │  }                     │
                    └─────────┬──────────────┘
                              │
                ┌─────────────▼────────────────┐
                │  Backend: query_compat()     │
                │  Function Receives Request   │
                └─────────────┬────────────────┘
                              │
    ┌─────────────────────────┴────────────────────────────┐
    │                  QUERY PROCESSING                     │
    └──────────────────────────┬────────────────────────────┘
                              │
                ┌─────────────▼─────────────┐
                │  Step 6: Identify/Select  │
                │  Document to Query        │
                │  - If doc_id provided:    │
                │    Use it                 │
                │  - Otherwise:             │
                │    Use first uploaded doc │
                └─────────────┬─────────────┘
                              │
                ┌─────────────▼──────────────────┐
                │  Step 7: Extract Document      │
                │  Content & Filename            │
                │  from document_store           │
                └─────────────┬──────────────────┘
                              │
                ┌─────────────▼──────────────────┐
                │  Step 8: Extract Resources     │
                │  (URLs) from Document          │
                │  Using Regex:                  │
                │  https?://[^\s\)"\]]+          │
                └─────────────┬──────────────────┘
                              │
    ┌─────────────────────────┴────────────────────────────┐
    │          STAGE 1: DOCUMENT CHECK                     │
    └──────────────────────────┬────────────────────────────┘
                              │
                ┌─────────────▼──────────────────┐
                │  Step 9: Create Prompt for     │
                │  Document Analysis             │
                │                                │
                │  Prompt:                       │
                │  "Can this question be         │
                │   answered from the document?  │
                │   Document: {filename}         │
                │   Question: {query}            │
                │   Content: {first 60k chars}"  │
                └─────────────┬──────────────────┘
                              │
                ┌─────────────▼──────────────────┐
                │  Step 10: Send Prompt to       │
                │  Gemini API (2.5-flash)        │
                │  model.generate_content(...)   │
                └─────────────┬──────────────────┘
                              │
                ┌─────────────▼──────────────────┐
                │  Step 11: Gemini Analyzes      │
                │  & Returns Response            │
                └─────────────┬──────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │  Check Response Prefix            │
            └────┬──────────────────────┬───────┘
                 │                      │
         ┌───────▼────────┐     ┌───────▼──────────┐
         │  Starts with   │     │  Doesn't Start   │
         │  "NOT_IN_      │     │  with "NOT_IN_   │
         │  DOCUMENT:"?   │     │  DOCUMENT:"?     │
         └───┬────────────┘     └───┬──────────────┘
             │                      │
             │ YES                  │ NO
             │                      │
    ┌────────▼────────────┐  ┌──────▼────────────┐
    │  STAGE 2: HYBRID    │  │  DOCUMENT ANSWER  │
    │  MODE TRIGGERED     │  │  FOUND!           │
    └────────┬────────────┘  └────┬──────────────┘
             │                     │
    ┌────────▼────────────────────┐│
    │  Step 12a: Create General   ││
    │  Knowledge Prompt:          ││
    │                             ││
    │  "Topic not in document.    ││
    │   Provide general advice    ││
    │   about: {query}"           ││
    │                             ││
    │  Send to Gemini API again   ││
    └────────┬────────────────────┘│
             │                     │
    ┌────────▼────────────┐        │
    │  Step 12b: Gemini   │        │
    │  Returns General    │        │
    │  Advice             │        │
    └────────┬────────────┘        │
             │                     │
    ┌────────▼────────────┐        │
    │  Combine Responses: │        │
    │                     │        │
    │  answer = (         │        │
    │    NOT_IN_DOCUMENT  │        │
    │    message +        │        │
    │    General Advice   │        │
    │  )                  │        │
    │                     │        │
    │  source_type =      │        │
    │  "hybrid"           │        │
    └────────┬────────────┘        │
             │                     │
             └──────────┬──────────┘
                        │
                ┌───────▼────────────┐
                │  Step 13: Prepare  │
                │  Response JSON:    │
                │  {                 │
                │    "success": true,│
                │    "answer": "..", │
                │    "query": "..",  │
                │    "source_doc": ..│
                │    "source_type":..│
                │    "resources": [] │
                │  }                 │
                └───────┬────────────┘
                        │
                ┌───────▼────────────┐
                │  Step 14: Send     │
                │  Response to       │
                │  Frontend (JSON)   │
                └───────┬────────────┘
                        │
    ┌───────────────────▼────────────────────┐
    │      FRONTEND: DISPLAY RESPONSE        │
    └──────────────────┬──────────────────────┘
                       │
            ┌──────────▼──────────┐
            │  Step 15: Remove    │
            │  "Thinking..."      │
            │  Message            │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  Step 16: Parse     │
            │  Response (Markdown)│
            │  - Convert          │
            │    **bold** →       │
            │    <strong>         │
            │  - Convert *italic* │
            │  - Format lists     │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  Step 17: Add Bot   │
            │  Message to Chat    │
            │  with Formatted     │
            │  Answer             │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  Step 18: Display   │
            │  in Chat UI:        │
            │  ✓ User Message     │
            │  ✓ AI Response      │
            │  ✓ Formatted        │
            │  ✓ Auto-scroll      │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  READY FOR NEXT     │
            │  QUESTION!          │
            └─────────────────────┘
```

**Key Points in Query Processing:**

1. **Two-Stage AI Analysis**:
   - First: Check if answer is in document
   - Second (if needed): Get general advice

2. **Resource Extraction**:
   - Automatically finds URLs in document
   - Includes them for context

3. **Hybrid Responses**:
   - Clear distinction between document content and general knowledge
   - User knows source of information

4. **Smart Formatting**:
   - Converts markdown to HTML
   - Preserves readability
   - Bold headers and lists

---

#### **Flow 3: Complete User Journey (End-to-End)**

```
START
  │
  ▼
┌──────────────────────┐
│ 1. OPEN APPLICATION  │
│ http://localhost:5000│
└──────────┬───────────┘
           │
  ┌────────▼────────┐
  │ 2. UPLOAD FILE  │
  │ (Flow 1 above)  │
  └────────┬────────┘
           │
  ┌────────▼────────┐
  │ 3. SUCCESS      │
  │ File in List    │
  └────────┬────────┘
           │
  ┌────────▼────────────┐
  │ 4. ASK QUESTION 1   │
  │ (Flow 2 above)      │
  └────────┬────────────┘
           │
  ┌────────▼────────────┐
  │ 5. SEE RESPONSE 1   │
  │ in Chat             │
  └────────┬────────────┘
           │
  ┌────────▼────────────┐
  │ 6. ASK QUESTION 2   │
  │ About Different     │
  │ Topic               │
  └────────┬────────────┘
           │
  ┌────────▼────────────┐
  │ 7. GET HYBRID       │
  │ RESPONSE            │
  │ (Doc + General)     │
  └────────┬────────────┘
           │
  ┌────────▼────────────┐
  │ 8. CONTINUE...      │
  │ Upload More Files   │
  │ Ask More Questions  │
  │ Preview Documents   │
  └────────┬────────────┘
           │
  ┌────────▼────────────┐
  │ 9. CLEAR DATA       │
  │ (Optional)          │
  │ Start Fresh         │
  └────────┬────────────┘
           │
          END

```

---

### Data Flow Diagrams

#### **Upload Data Flow**

```
USER BROWSER
    │
    ├─ File Selected
    ├─ FormData Created
    ├─ POST /upload
    │   │
    │   ▼
    └─→ FLASK BACKEND
        │
        ├─ Receive Files
        ├─ Validate (type, size)
        ├─ Extract Text
        │   │
        │   ├─→ PDF: PyPDF2
        │   ├─→ DOCX: python-docx
        │   └─→ TXT: read()
        │
        ├─ Store in Memory
        │   document_store = {
        │     "name": content,
        │     "size": bytes
        │   }
        │
        └─ Return JSON Response
            │
            ▼
        BROWSER
        │
        ├─ Parse Response
        ├─ Update File List
        ├─ Show Success Message
        └─ Ready for Queries
```

#### **Query Data Flow**

```
USER INPUT
    │
    ├─ Question Typed
    ├─ JSON Created
    ├─ POST /query
    │   │
    │   ▼
    └─→ FLASK BACKEND
        │
        ├─ Parse Query
        ├─ Get Document
        ├─ Extract Resources
        │
        ├─ STAGE 1: Doc Check
        │   │
        │   ├─ Create Prompt
        │   ├─ Call Gemini API
        │   └─ Receive Response
        │
        ├─ Check: In Document?
        │   │
        │   ├─ YES → Return Answer
        │   │       source_type: "document"
        │   │
        │   └─ NO → STAGE 2
        │       │
        │       ├─ Create General Prompt
        │       ├─ Call Gemini API
        │       ├─ Receive Advice
        │       │
        │       └─ Combine Responses
        │           source_type: "hybrid"
        │
        └─ Return JSON Response
            │
            ▼
        BROWSER
        │
        ├─ Remove "Thinking..."
        ├─ Parse Markdown
        ├─ Format Text
        ├─ Add to Chat
        ├─ Auto-scroll
        └─ Ready for Next Question
```

---

### State Management

```
APPLICATION STATE

┌─────────────────────────────────┐
│  Browser (Frontend)             │
├─────────────────────────────────┤
│                                 │
│  Chat History:                  │
│  [                              │
│    {user: "question 1"},        │
│    {bot: "answer 1"},           │
│    {user: "question 2"},        │
│    {bot: "answer 2"}            │
│  ]                              │
│                                 │
│  File List:                     │
│  ["Resume_ASR.pdf", ...]        │
│                                 │
└─────────────────────────────────┘
           │
           │ (Persists in Page)
           │ (Lost on Refresh)
           │
┌─────────────────────────────────┐
│  Server (Backend - app.py)      │
├─────────────────────────────────┤
│                                 │
│  document_store = {             │
│    "Resume_ASR.pdf": {          │
│      "filename": "...",         │
│      "content": "...",          │
│      "upload_time": "...",      │
│      "size": 125000             │
│    }                            │
│  }                              │
│                                 │
│  (Persists During Runtime)      │
│  (Lost on App Restart)          │
│                                 │
└─────────────────────────────────┘
```

---

### Processing Timeline Example

```
User: "Upload Resume_ASR.pdf"
⏱️ 0.0s: File selected, upload starts
⏱️ 0.2s: Network transfer completes
⏱️ 0.3s: Backend receives file
⏱️ 0.5s: PyPDF2 extracts text
⏱️ 0.8s: Document stored in memory
⏱️ 0.9s: Response sent to frontend
⏱️ 1.0s: UI updated, file appears in list

User: "How can this be improved?"
⏱️ 0.0s: Question typed, sent to backend
⏱️ 0.1s: Backend receives query
⏱️ 0.2s: Document retrieved from memory
⏱️ 0.3s: Prompt created
⏱️ 0.4s: Gemini API called (Stage 1)
⏱️ 2.5s: Gemini responds (not in document)
⏱️ 2.6s: Stage 2 triggered
⏱️ 2.7s: General prompt created
⏱️ 2.8s: Gemini API called (Stage 2)
⏱️ 5.2s: Gemini responds with advice
⏱️ 5.3s: Response formatted
⏱️ 5.4s: Response sent to frontend
⏱️ 5.5s: UI updated, answer displayed
⏱️ 5.6s: User sees complete response

Total Query Time: ~5.6 seconds
```



---

## API Endpoints

### Document Management

#### POST `/upload`
Upload one or multiple documents

**Request:**
```
Content-Type: multipart/form-data
Body: files=[file1, file2, ...]
```

**Response:**
```json
{
  "success": true,
  "message": "Uploaded 1 file(s)",
  "results": [
    {
      "success": true,
      "filename": "Resume_ASR.pdf",
      "size": 125000,
      "doc_id": "Resume_ASR.pdf"
    }
  ]
}
```

#### POST `/clear_storage`
Clear all uploaded documents and files

**Response:**
```json
{
  "success": true,
  "message": "Storage cleared"
}
```

#### GET `/uploads/<filename>`
Serve uploaded documents

**Response:** File with appropriate MIME type (PDF, DOCX, TXT, etc.)

### Query System

#### POST `/query`
Ask a question about uploaded documents

**Request:**
```json
{
  "query": "How can this be improved?",
  "doc_id": "optional_document_id"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Based on general knowledge and best practices...",
  "query": "How can this be improved?",
  "source_document": "Resume_ASR.pdf",
  "source_type": "hybrid",
  "resources_found": ["https://www.json.org/json-en.html"]
}
```

#### GET `/preview/<filename>`
Preview generated files (PDFs, HTML, etc.)

**Response:** File with appropriate MIME type

### Alternative API Routes

#### POST `/api/upload`
Alternative upload endpoint (same as `/upload`)

#### POST `/api/ask`
Alternative query endpoint (requires `question` and `doc_id`)

#### GET `/api/documents`
Get list of all uploaded documents

#### DELETE `/api/delete/<doc_id>`
Delete a specific document

---

## File Structure

```
CloneBookLLM/
├── app.py                    # Main Flask application
├── agent.py                  # RAG Agent (for future use)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create manually)
├── .gitignore               # Git ignore rules
│
├── templates/
│   └── index.html           # Main HTML template
│
├── static/
│   ├── script.js            # Frontend JavaScript
│   ├── style.css            # CSS styling
│   ├── uploads/             # User uploaded files
│   └── outputs/             # Generated outputs
│
├── uploads/                 # Backend upload storage
│   └── [uploaded files]
│
└── README.md                # This documentation
```

---

## Usage Guide

### 1. **Upload a Document**

1. Open http://localhost:5000
2. Click "Choose Files" or drag & drop
3. Select your document (PDF, TXT, DOCX, MD)
4. Click "Upload"
5. Wait for confirmation message

### 2. **Ask Questions**

1. Type your question in the chat input
2. Press Enter or click Send
3. AI will analyze the document
4. Response appears in chat with:
   - Direct answers if found in document
   - General advice if topic not covered
   - Resource references when applicable

### 3. **View Document Details**

1. Uploaded files appear in the file list
2. Click on filename to preview
3. View content in modal
4. Download if needed

### 4. **Clear Data**

- Click "Clear" or refresh page to clear all data
- Documents and chat history will be cleared

---

## Technical Details

### Document Processing

**PDF Processing:**
```python
PyPDF2.PdfReader(file)
# Extracts text from each page
```

**DOCX Processing:**
```python
from docx import Document
# Extracts paragraphs and text
```

**TXT/MD Processing:**
```python
# Direct file read with UTF-8 encoding
```

### Gemini API Integration

**Two-Stage Query Process:**

**Stage 1: Document Content Check**
```python
prompt = f"""
Analyze if this question can be answered from the document:
Question: {query}
Document Content: {doc_content[:60000]}

If answer is in document: Provide answer
If not: Start with "NOT_IN_DOCUMENT: "
"""
response = model.generate_content(prompt)
```

**Stage 2: General Knowledge (if needed)**
```python
if response.startswith("NOT_IN_DOCUMENT:"):
    prompt = f"""
    Topic not in document. Provide general advice:
    Question: {query}
    """
    response = model.generate_content(prompt)
```

### In-Memory Storage

Documents stored in dictionary:
```python
document_store = {
    "Resume_ASR.pdf": {
        "filename": "Resume_ASR.pdf",
        "content": "full text content...",
        "upload_time": "2025-11-27T20:53:22",
        "size": 125000
    }
}
```

**Advantages:**
- Fast access
- No database needed

**Limitations:**
- Data lost on app restart
- Limited to available RAM

---

## Error Handling

The system handles:

1. **Invalid file types** - Returns error message
2. **File size exceeded** - Returns 413 error
3. **Missing API key** - Exits with error
4. **Network errors** - Returns error response
5. **Malformed requests** - Returns 400 error

---

## Performance Considerations

1. **Document Size**: Currently processes up to 60,000 characters
2. **Query Speed**: ~2-5 seconds depending on Gemini API
3. **Concurrent Users**: Limited by Flask (development mode)
4. **Memory Usage**: ~50MB base + document sizes

---

## Future Enhancements

1. **Database Integration** - Persistent storage
2. **User Authentication** - Multi-user support
3. **Advanced RAG** - Vector embeddings and ChromaDB
4. **File Export** - Save conversations as PDF
5. **Multiple Documents** - Cross-document queries
6. **Production Deployment** - Gunicorn/Nginx setup
7. **Caching** - Improve response times
8. **Analytics** - Track usage patterns

---

## Troubleshooting

### Dependency Issues

#### Issue: "AttributeError: type object 'GenerationConfig' has no attribute 'Modality'"

**Cause:** Version mismatch between `google-generativeai` and `langchain-google-genai`

**Solution:**
```bash
pip install --upgrade google-generativeai langchain-google-genai
```

Ensure versions are compatible:
- `google-generativeai>=0.7.0`
- `langchain-google-genai>=0.2.0`

#### Issue: "No module named 'google.generativeai'"

**Solution:**
```bash
pip install google-generativeai>=0.7.0
```

#### Issue: "ModuleNotFoundError: No module named 'sentence_transformers'"

**Solution:**
```bash
pip install sentence-transformers
```

### API and Authentication

#### Issue: "GOOGLE_API_KEY not found"

**Solution:**
1. Create `.env` file in project root
2. Add: `GOOGLE_API_KEY=your_key_here`
3. Restart app
4. Verify key has Generative AI API enabled

#### Issue: "403 Forbidden - API key not authorized"

**Solution:**
- Check API key is valid
- Verify Generative AI API is enabled in Google Cloud Console
- Check API quota limits

### Agent-Specific Issues

#### Issue: "WARNING: Could not import RAGAgent. Using basic Q&A mode."

**Cause:** RAGAgent initialization failed

**Debugging:**
```python
# Check app startup logs for the actual error
python app.py 2>&1 | grep "RAGAgent"
```

**Common Solutions:**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check ChromaDB installation: `pip install chromadb`
- Verify LangChain version compatibility

#### Issue: Agent not selecting correct tool

**Solution:**
1. Check agent verbosity logs in console
2. Verify tool descriptions are clear
3. Try rephrasing query more explicitly

**Example:**
- ❌ "Make a PPT" → ✅ "Create a presentation"
- ❌ "Sounds" → ✅ "Generate audio file"

### Vector Store Issues

#### Issue: "Chroma vector store not initialized"

**Cause:** No documents uploaded yet

**Solution:**
1. Upload at least one document
2. Wait for RAG pipeline initialization
3. Check console for "✅ RAG Initialized" message

#### Issue: Slow vector search

**Solution:**
- Reduce chunk overlap in `agent.py`
- Limit retrieval to k=3 (default)
- Use smaller embedding model

### File-Related Issues

#### Issue: "File not found on server"

**Solution:**
- Ensure `uploads/` folder exists
- Check file permissions: `chmod 755 uploads/`
- Verify `/uploads/` route is accessible

#### Issue: "Could not extract text from file"

**Solution:**
- Ensure file format is supported (PDF, DOCX, TXT, MD, PPT)
- Check file is not corrupted
- Verify file size < 50MB

#### Issue: Generated files (PPT/Audio) not created

**Solution:**
- Verify `static/outputs/` folder exists
- Check folder write permissions
- Ensure gTTS and python-pptx installed

### Chat Interface Issues

#### Issue: Chat messages disappearing

**Solution:**
- Check browser console for errors
- Clear browser cache
- Verify app is still running
- Check network tab for API errors

#### Issue: Markdown formatting not rendering

**Solution:**
- Verify markdown syntax in your message
- Check browser supports HTML5
- Clear browser cache and reload

#### Issue: "Thinking..." message stuck indefinitely

**Solution:**
1. Check if Gemini API is responsive
2. Monitor API quota/limits
3. Try simpler query
4. Restart app and retry

### Performance Issues

#### Issue: Slow query responses

**Causes:**
- Gemini API latency (2-5s typical)
- Large document processing
- Slow network connection

**Optimization:**
- Reduce document size before upload
- Use smaller chunks in RAG
- Ensure internet connection is stable

#### Issue: High memory usage

**Solution:**
- Clear old uploads periodically
- Restart app to reset in-memory storage
- Monitor with: `top` or `htop`

### Network Issues

#### Issue: "Connection refused" on localhost:5000

**Solution:**
1. Verify app is running: `ps aux | grep app.py`
2. Check port 5000 is not in use: `lsof -i :5000`
3. Change port if needed: modify `app.run()` in app.py

#### Issue: "CORS" or cross-origin errors

**Solution:**
- Ensure frontend and backend on same origin
- Check browser console for specific errors
- Verify Flask is serving from correct domain

---

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Submit pull request

---

## License

This project is licensed under the MIT License.

---

## Contact

For questions or support, contact: batman@example.com

---

## Changelog

### Version 2.0 (2025-11-28)
- **Major Architecture Update:**
  - ✅ Integrated LangChain Agent system
  - ✅ Added 4-tool agent with intelligent tool selection
  - ✅ Wired agent tool-use to chat interface
  - ✅ Implemented ChromaDB vector store for RAG
  - ✅ Added HuggingFace embeddings (all-MiniLM-L6-v2)
  - ✅ PPT generation with PPTX export
  - ✅ Audio generation with gTTS
  - ✅ Web search integration with DuckDuckGo

- **Features:**
  - Agent-based query processing with tool selection
  - Multi-stage reasoning (REACT loop)
  - Semantic similarity search with top-k retrieval
  - Conversation memory for multi-turn interactions
  - Graceful fallback to basic RAG if agent fails
  - Enhanced error handling and logging

- **Dependencies:**
  - langchain 0.1.0+
  - langchain-google-genai 0.2.0+
  - langchain-huggingface
  - langchain-community
  - chromadb 0.4.10+
  - sentence-transformers
  - gTTS 2.4.0+

- **API Changes:**
  - POST `/query` now returns `agent_used`, `retrieval_method`, `source_type`
  - Added agent reasoning logs to console output

### Version 1.0 (2025-11-27)
- Initial release
- Document upload and processing
- Hybrid Q&A system (document + general knowledge)
- Chat interface with formatting
- File preview system
- Resource extraction

---

**Last Updated**: 28 November 2025
