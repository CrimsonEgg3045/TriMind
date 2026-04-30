# Tri Mind — Multi-Agent AI Study Assistant

Tri Mind is an advanced, multi-agent AI study assistant designed to provide comprehensive, easy-to-understand explanations for a variety of topics. By utilizing an orchestrator to coordinate multiple specialized AI agents, Tri Mind delivers rich, synthesized responses that include clear explanations, accurate mathematical derivations, and relevant visual aids.

## 🚀 Features

- **Multi-Agent Architecture**: Uses an asyncio-based orchestrator to run multiple AI agents in parallel for maximum speed and efficiency.
- **Explanation Agent**: Breaks down complex concepts into intuitive, easy-to-digest explanations. Powered by DeepSeek.
- **Math Agent**: Handles complex mathematical derivations and problem-solving. Powered by OpenRouter.
- **Visual Agent**: Generates diagrams (SVG/Canvas) or images to visually represent concepts. Integrated with a custom Cloudflare Worker and DeepSeek.
- **Synthesizer Agent**: Combines the outputs from the Explanation, Math, and Visual agents into a single, cohesive tutorial-like response. Powered by DeepSeek.
- **Demo Mode Caching**: Built-in caching system for fast demonstration and reduced API costs.
- **Fault Tolerance**: Robust error handling and timeouts ensure the system degrades gracefully if a specific agent encounters an issue.

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3
- **Frontend**: Vanilla HTML/CSS/JS (served as static files)
- **AI Providers**: DeepSeek API, OpenRouter API
- **Concurrency**: `asyncio` for parallel agent execution

## 📦 Installation & Setup

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd Code_Rush
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**:
   Copy the example environment file and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and add your keys:
   ```env
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   CF_WORKER_URL=https://ai-image-worker.<your_name>.workers.dev
   ```

## 🚀 Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

The application will be available at:
- **Frontend / UI**: [http://localhost:8000/](http://localhost:8000/)
- **API Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🧠 Architecture Overview

When a user submits a query via the frontend:
1. The **Orchestrator** (`orchestrator.py`) receives the query.
2. It simultaneously dispatches the query to the **Explanation**, **Math**, and **Visual** agents using `asyncio.gather`.
3. Once the sub-agents return their results (or timeout), the **Synthesizer** agent formats and combines the information into a unified response.
4. The backend returns the final synthesized JSON response (including any generated diagrams or image URLs) to the frontend.

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
