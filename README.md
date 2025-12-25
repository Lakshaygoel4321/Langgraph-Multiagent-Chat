```markdown
# LangGraph Multi-Agent Chat System

A production-ready, full-stack AI application built with **LangGraph**, **FastAPI**, and **Next.js**.  
The system orchestrates specialized **business**, **research**, and **technical** agents with:

- Multi-step reasoning and routing
- Web search–augmented synthesis
- Conversation memory using a checkpointer
- Streaming and non-streaming responses
- Clean, modular architecture suitable for real-world projects

---

## Features

- **Multi-Agent Architecture**
  - Supervisor agent routes questions to **business**, **research**, or **technical** specialists.
  - Synthesis agents combine LLM output with web search for more reliable answers.
  - Validator agent scores answer quality (0–10) before returning to the user.

- **Memory & Threading**
  - Conversation-level memory using LangGraph checkpointer.
  - `thread_id` support to maintain separate chat sessions.
  - Ability to retrieve state and history per thread.

- **Full-Stack Implementation**
  - **Backend**: FastAPI + LangGraph + Groq LLM + Tavily search.
  - **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS.
  - Streaming via Server-Sent Events (SSE) for incremental UI updates.

- **Production-Ready Design**
  - Clear separation of concerns (agents, synthesis, validators, routers, graph, config).
  - Environment-based configuration.
  - CORS, logging, and basic security headers.
  - `.gitignore` tuned for Python + Node.js monorepo.

---

## Tech Stack

### Backend

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Orchestration**: LangGraph
- **LLM Provider**: Groq (e.g., `llama-3.3-70b-versatile`)
- **Search**: Tavily
- **HTTP Server**: Uvicorn

### Frontend

- **Framework**: Next.js (App Router, TypeScript)
- **UI**: React, Tailwind CSS
- **HTTP Client**: Axios + Fetch (for SSE)
- **Icons & UI Enhancements**: `lucide-react`, `react-markdown`

---

## Project Structure

```
Langgraph-Project/
├── backend/
│   ├── api/
│   │   └── routes/
│   │       └── agent.py        # FastAPI endpoints (ask, stream, history, state, status)
│   ├── config/
│   │   ├── settings.py         # Environment & config
│   │   └── prompts.py          # System prompts (supervisor, agents, synthesis, validator)
│   ├── src/
│   │   ├── agents/             # Business, research, technical agents
│   │   ├── synthesis/          # Synthesis agents & base class
│   │   ├── validators/         # Validator agent
│   │   ├── routers/            # Supervisor & routing logic
│   │   ├── utils/              # State, schemas, tools (Tavily)
│   │   └── graph/
│   │       └── workflow.py     # LangGraph StateGraph construction & memory
│   ├── .env                    # Backend environment (not committed)
│   ├── requirements.txt
│   └── main.py                 # FastAPI entrypoint
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx        # Main chat page
    │   │   ├── layout.tsx
    │   │   └── globals.css
    │   ├── components/
    │   │   ├── ChatInterface.tsx
    │   │   ├── MessageList.tsx
    │   │   └── InputForm.tsx (if used)
    │   ├── services/
    │   │   └── api.ts          # API client (ask, stream, history, state)
    │   └── types/
    │       └── index.ts        # Shared TypeScript types
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.js
    └── .env.local              # Frontend environment (not committed)
```

---

## Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **Git**
- Accounts / API keys for:
  - **Groq** (LLM)
  - **Tavily** (search)

---

## Backend Setup (FastAPI + LangGraph)

1. ### Navigate to backend

```
cd backend
```

2. ### Create & activate virtual environment

```
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

3. ### Install dependencies

```
pip install -r requirements.txt
```

4. ### Configure environment variables

Create `.env` in `backend/`:

```
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

5. ### Run backend server

```
python main.py
```

Backend will be available at:

- API Root: `http://localhost:8000/`
- Health: `http://localhost:8000/health`
- Main Agent Endpoint: `POST http://localhost:8000/api/v1/ask`

---

## Frontend Setup (Next.js)

1. ### Navigate to frontend

```
cd frontend
```

2. ### Install dependencies

```
npm install
# or
yarn install
```

3. ### Configure frontend environment

Create `.env.local` in `frontend/`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. ### Run Next.js dev server

```
npm run dev
# or
yarn dev
```

Frontend will be available at:

- `http://localhost:3000/`

---

## How It Works

### 1. Request Flow

1. User enters a question in the Next.js UI.
2. Frontend calls `POST /api/v1/ask` (or `/ask/stream` for streaming).
3. FastAPI passes the question (and `thread_id`) into the LangGraph `AgentWorkflow`.
4. LangGraph executes:
   - **SupervisorAgent** → classify: business / research / technical.
   - Corresponding **domain agent** generates a draft answer.
   - **Synthesis agent** merges LLM answer with Tavily web search.
   - **ValidatorAgent** scores the final answer (0–10).
5. Final answer, classification, and confidence score return to frontend.
6. UI displays formatted response, including type and confidence.

### 2. Memory & Threads

- Each conversation uses a `thread_id` (stored in session storage on the frontend).
- LangGraph’s checkpointer (MemorySaver) persists state between calls.
- You can:
  - Query history: `GET /api/v1/history/{thread_id}`
  - Query current state: `GET /api/v1/state/{thread_id}`

---

## API Endpoints

### `POST /api/v1/ask`

Submit a question (non-streaming).

**Request:**

```
{
  "question": "What is SWOT analysis, and how is it used in strategic planning?",
  "thread_id": "thread-123-abc",
  "stream": false
}
```

**Response:**

```
{
  "question": "What is SWOT analysis, and how is it used in strategic planning?",
  "answer": "…",
  "confidence_score": "9",
  "classifier": "business",
  "reasoning": "…",
  "timestamp": "2025-12-25T12:00:00Z",
  "thread_id": "thread-123-abc"
}
```

### `POST /api/v1/ask/stream`

Same as `/ask`, but returns **Server-Sent Events (SSE)** for streaming partial updates.

### `GET /api/v1/history/{thread_id}`

Returns recent message history for a given thread.

### `GET /api/v1/state/{thread_id}`

Returns the current LangGraph state snapshot for debugging/inspection.

### `GET /api/v1/status`

Returns metadata about the service (available agents, features, model name).

---

## Development Workflow

### Recommended Steps

- **Backend**
  - Modify prompts in `backend/config/prompts.py`.
  - Add/extend agents in `backend/src/agents/`.
  - Adjust routing in `backend/src/routers/supervisor.py`.
  - Modify graph logic in `backend/src/graph/workflow.py`.

- **Frontend**
  - Edit UI in `frontend/src/app/page.tsx` and `frontend/src/components/`.
  - Update API interaction in `frontend/src/services/api.ts`.
  - Customize styling with Tailwind in `globals.css` and `tailwind.config.js`.

---

## Testing

You can add tests under:

- Backend: `backend/tests/`
- Frontend: `frontend/__tests__/` or `frontend/src/__tests__/`

Example backend test (pytest):

```
cd backend
pytest
```

---

## Deployment

### Backend

- Containerize with Docker or run via a process manager (e.g., systemd, PM2 for Node side).
- Reverse proxy with Nginx or Caddy.
- Ensure environment variables are set on the server (GROQ, Tavily).

### Frontend

- Build and deploy:

```
cd frontend
npm run build
npm run start
```

- Or deploy via platforms like Vercel, Netlify, or your own Node server.

---

## Roadmap Ideas

- Add authentication and per-user thread segregation.
- Plug in vector database (e.g., PostgreSQL + pgvector, Pinecone) for RAG.
- Enhance UI with chat history list and multi-thread management.
- Add more specialized agents (e.g., finance, legal, marketing).
- Integrate analytics and logging for observability.

---

## Contributing

1. Fork the repository.
2. Create a new feature branch:
   ```
   git checkout -b feature/new-agent
   ```
3. Commit your changes with clear messages.
4. Open a Pull Request describing:
   - What you changed
   - Why it’s useful
   - How to test it

---

## License

This project is released under the **MIT License**.  
You are free to use, modify, and distribute it with proper attribution.

---

## Contact

For questions, suggestions, or collaboration:

- GitHub: `https://github.com/<your-username>/Langgraph-Project`
- Email: `<your-email-if-you-want>`

---

> This repository is designed as a solid **template** for building real-world LangGraph-based multi-agent applications with a modern full-stack setup.
```

You can now:

1. Save this content as `README.md` in your repo root.
2. Replace placeholders like `<your-username>` or `<your-email-if-you-want>` if you want.
3. Commit and push:

```powershell
git add README.md
git commit -m "Add professional README"
git push origin main
```

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/107878637/42243ec3-005b-4c49-8599-8d2e449e4014/paste.txt)
