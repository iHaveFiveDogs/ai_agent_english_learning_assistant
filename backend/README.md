# Backend for Article AI Agent

This backend powers the Article AI Agent, providing advanced English learning assistance using AI-driven services and APIs.

## Features
- AI-powered text explanation, summarization, and persona management
- Modular agent and service architecture
- RESTful API powered by FastAPI
- Integration with LangChain for advanced language processing
- Extensible and easy to maintain

## Tech Stack
- **Python 3.x**
- **FastAPI**: High-performance web framework for building APIs
- **LangChain**: Framework for developing applications powered by large language models
- **ChromaDB**: Vector database for storing embeddings (if used)
- Other dependencies as listed in `requirements.txt`

## Directory Structure
```
ai_service/           # AI agents for various NLP tasks
services/             # Core business logic and reusable services
routes/               # FastAPI route definitions
models/               # Data models and schemas
system_maintainace/   # Maintenance scripts and tests
db/                   # Database files and migrations
chroma_db/            # Vector database files
main.py               # FastAPI application entry point
requirements.txt      # Python dependencies
```

## Getting Started
1. **Clone the repository**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the FastAPI server**
   ```bash
   uvicorn main:app --reload
   ```
4. **Access the API docs**
   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

## Usage
- Use the provided API endpoints for article upload, explanation, and summarization.
- Refer to the `ai_service` and `services` directories for modular agent/service usage.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
[MIT](LICENSE) (or specify your license here)

## Contact
For questions or support, contact the project maintainer.
