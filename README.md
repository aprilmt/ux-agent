# UX AI Agent

A specialized AI agent for UX workflow, thinking, and writing assistance.

## Features

- **UX Workflow Specialist**: Process optimization and methodologies
- **UX Strategic Thinker**: User psychology and design thinking
- **UX Writing Expert**: Content strategy and microcopy
- **Job Story Framework**: Iterative refinement process for user stories

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python ollama_llm_backend.py
```

3. Access the application:
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Deployment on Render

1. **Connect Repository**: Link your GitHub repository to Render
2. **Configure Service**:
   - Name: `ux-agent`
   - Language: `Docker`
   - Region: `Oregon (US West)`
3. **Set Environment Variables**:
   - `OLLAMA_BASE_URL`: `http://localhost:11434`
   - `OLLAMA_MODEL`: `mistral:latest`
   - `PORT`: `8000` (auto-set by Render)
4. **Deploy**: Click "Create Web Service"

## Environment Variables

- `OLLAMA_BASE_URL`: Ollama service URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Model to use (default: mistral:latest)
- `PORT`: Server port (default: 8000)

## API Endpoints

- `GET /`: Main application interface
- `GET /health`: Health check
- `POST /api/ux-agent/chat`: Chat with the AI agent
- `GET /api/ux-agent/chat-history/{conversation_id}`: Get chat history