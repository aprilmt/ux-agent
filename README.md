# UX AI Agent

A specialized AI agent for UX workflow, thinking, and writing assistance powered by Ollama Cloud and GPT-OSS-120B model.

## ✨ Features

- **UX Workflow Specialist**: Process optimization and methodologies
- **UX Strategic Thinker**: User psychology and design thinking  
- **UX Writing Expert**: Content strategy and microcopy
- **Job Story Framework**: Iterative refinement process for user stories
- **Comprehensive UX Knowledge**: Integrated knowledge from UX resources and best practices
- **Smart Fallback System**: Intelligent responses when Ollama is unavailable
- **Dynamic UI**: Responsive design with adaptive logo sizing
- **Conversation Context**: Maintains chat history for better follow-up responses

## 🌐 Live Demo

**Deployed on Render**: https://ux-agent-euub.onrender.com/

## 🚀 Local Development

### Prerequisites
- Python 3.9+
- Ollama v0.12+ (for cloud models)

### Setup Steps

1. **Install Ollama** (if not already installed):
```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

2. **Start Ollama service**:
```bash
ollama serve
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Start the server**:
```bash
python ollama_llm_backend.py
```

5. **Access the application**:
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ☁️ Cloud Model Usage

This application uses **Ollama Cloud** with the `gpt-oss:120b-cloud` model, providing:
- **120 billion parameters** for sophisticated responses
- **No local model downloads** required
- **Datacenter-grade performance**
- **Privacy-focused** (no data retention)

## 🐳 Deployment on Render

1. **Connect Repository**: Link your GitHub repository to Render
2. **Configure Service**:
   - Name: `ux-agent`
   - Language: `Docker`
   - Region: `Oregon (US West)`
3. **Set Environment Variables**:
   - `OLLAMA_BASE_URL`: `http://localhost:11434`
   - `OLLAMA_MODEL`: `gpt-oss:120b-cloud`
   - `PORT`: `8000` (auto-set by Render)
4. **Deploy**: Click "Create Web Service"

## ⚙️ Environment Variables

- `OLLAMA_BASE_URL`: Ollama service URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Model to use (default: gpt-oss:120b-cloud)
- `PORT`: Server port (default: 8000)

## 🔌 API Endpoints

- `GET /`: Main application interface
- `GET /health`: Health check
- `POST /api/ux-agent/chat`: Chat with the AI agent
- `GET /api/ux-agent/chat-history/{conversation_id}`: Get chat history
- `DELETE /api/ux-agent/chat-history/{conversation_id}`: Clear chat history

## 🛠️ Technology Stack

- **Backend**: FastAPI + Python
- **AI Model**: GPT-OSS-120B via Ollama Cloud
- **Frontend**: HTML/CSS/JavaScript with responsive design
- **Deployment**: Docker + Render
- **Knowledge Base**: Integrated UX resources and PDF content
- **Styling**: Modern CSS with smooth transitions and animations

## 🎨 UI/UX Features

- **Dynamic Logo Sizing**: Adapts based on chat state (80px → 60px)
- **Smooth Transitions**: Animated responses and state changes
- **Responsive Design**: Works on desktop and mobile devices
- **Consistent Formatting**: Clean text formatting with proper headings
- **Smart Spacing**: Optimized layout for better readability
- **Conversation Context**: Maintains chat history for contextual responses

## 📚 Knowledge Base

The agent is trained on comprehensive UX resources including:
- UX workflow methodologies
- Job story development frameworks
- User research best practices
- B2B UX strategies
- Usability testing techniques
- Product analytics integration

## 🤝 Contributing

This project is designed for UX professionals and teams. Feel free to submit issues or feature requests!

## 📄 License

Created by April Ma for UX professionals and teams.
