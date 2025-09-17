# UX AI Agent

A specialized AI agent for UX workflow, thinking, and writing assistance powered by Ollama and Gemma-2B instruct model.

## Features

- **UX Workflow Specialist**: Process optimization and methodologies
- **UX Strategic Thinker**: User psychology and design thinking  
- **UX Writing Expert**: Content strategy and microcopy
- **Job Story Framework**: Iterative refinement process for user stories
- **Comprehensive UX Knowledge**: Integrated knowledge from UX resources and best practices
- **Smart Fallback System**: Intelligent responses when Ollama is unavailable

## Live Demo

🌐 **Deployed on Render**: https://ux-agent-euub.onrender.com/

## Local Development

1. **Install Ollama** (if not already installed):
```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

2. **Pull the required model**:
```bash
ollama pull gemma:2b-instruct
```

3. **Start Ollama service**:
```bash
ollama serve
```

4. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

5. **Start the server**:
```bash
python ollama_llm_backend.py
```

6. **Access the application**:
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
   - `OLLAMA_MODEL`: `gemma:2b-instruct`
   - `PORT`: `8000` (auto-set by Render)
4. **Deploy**: Click "Create Web Service"

## Environment Variables

- `OLLAMA_BASE_URL`: Ollama service URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Model to use (default: gemma:2b-instruct)
- `PORT`: Server port (default: 8000)

## API Endpoints

- `GET /`: Main application interface
- `GET /health`: Health check
- `POST /api/ux-agent/chat`: Chat with the AI agent
- `GET /api/ux-agent/chat-history/{conversation_id}`: Get chat history

## Technology Stack

- **Backend**: FastAPI + Python
- **AI Model**: Gemma-2B instruct via Ollama
- **Frontend**: HTML/CSS/JavaScript
- **Deployment**: Docker + Render
- **Knowledge Base**: Integrated UX resources and PDF content

## Contributing

This project is designed for UX professionals and teams. Feel free to submit issues or feature requests!