# AI-Insurance-Claim-Engine

A modern, large language model (LLM)-powered system for automated adjudication of insurance claims. This engine processes raw user queries about insurance claims, retrieves relevant clauses from policy documents, and determines claim approval or rejection with clear, clause-referenced justifications.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Development](#development)
- [Technologies Used](#technologies-used)
- [License](#license)

---

## Overview

**AI-Insurance-Claim-Engine** streamlines and automates the process of evaluating insurance claims using state-of-the-art LLMs and Retrieval Augmented Generation (RAG). Given a user’s claim query, it:

1. Parses and extracts structured details from the query.
2. Finds relevant policy clauses using a vector search.
3. Adjudicates claim validity and computes payout, providing justification mapped to source clauses.

The engine is designed for extensibility, robust logging, and explainable output—making it valuable for insurance operations requiring transparency and auditability.

---

## Features

- **End-to-End Claim Adjudication**: From natural language input to detailed, structured decision.
- **RAG Architecture**: Retrieves precise clauses from vectorized policy document storage.
- **LLM-Based Reasoning**: Employs cutting-edge large language models for entity extraction and decision logic.
- **Web Interface**: Minimal Flask-based web UI for interactive queries.
- **Detailed, Explainable Output**: Presents approval/rejection, payout, and clear, clause-backed justification.
- **Session Management**: Maintains conversational context and chat history.

---

## Architecture

**Key Flow:**
1. **User Query Input**: Typed via web UI.
2. **Entity Parsing**: LLM parses claim details from the query.
3. **Clause Retrieval**: Vector store indexes policy documents; retrieves relevant clauses.
4. **Decision Making**: LLM reasons over claim details and policy clauses, outputs structured JSON.
5. **Result Display**: Response rendered in chat with breakdown and justifications.

**Main Components:**
```
- app/
  - application.py         # Flask entry point and main controller
  - components/
      - retriever.py       # End-to-end orchestration: parsing, retrieval, and decision logic
      - pdf_loader.py      # Loads and preprocesses policy PDFs
      - llm.py             # Model loading/configuration (e.g., Groq Llama3)
      - vector_store.py    # Vector DB (FAISS) loader for semantic search
      - data_loader.py     # Data ingestion and chunking support
      - embeddings.py      # Embedding generation for chunks
      - ...
  - config/
      - config.py          # Environment and system configuration
  - common/
      - logger.py, custom_exception.py    # Robust logging and error handling
  - templates/index.html   # Main HTML interface
- data/                    # Example PDF policy files
- vectorstore/db_faiss/    # Vector index for fast clause retrieval
- requirements.txt         # Python dependencies
- Dockerfile               # Containerization configuration
```

---

## Installation

### Prerequisites

- Python 3.10+
- [Groq](https://groq.com/) API key (for LLM access)
- [Hugging Face](https://huggingface.co/) token (optional, for local LLMs)
- Docker (optional)

### Quick Start (Recommended)

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Devmangukiya/AI-Insurance-Claim-Engine.git
   cd AI-Insurance-Claim-Engine
   ```

2. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set environment variables:**  
   Create a `.env` file or export the necessary variables:
   ```
   GROQ_API_KEY=<your_groq_api_key>
   HF_TOKEN=<your_huggingface_token>   # if using Hugging Face models
   ```

4. **Place PDF Policy Documents**
   - Place your policy `.pdf` files inside the `data/` directory.

5. **Run the App:**
   ```sh
   python app/application.py
   ```
   The app runs by default on `http://0.0.0.0:5000`.

### Docker

1. **Build the Docker image:**
   ```sh
   docker build -t ai-insurance-claim-engine .
   ```
2. **Run the container:**
   ```sh
   docker run -p 5000:5000 --env-file=.env ai-insurance-claim-engine
   ```

---

## Usage

- Navigate to [http://localhost:5000](http://localhost:5000).
- Enter natural language queries about insurance claims, e.g.:
  ```
  A 35-year-old male requesting a claim for a knee replacement after 2 years of policy tenure.
  ```
- The system responds with a "Decision", "Payout Amount", and "Justification Details," each mapping reasons to specific policy clauses.

- Use the `/clear` endpoint or 'Clear' button to reset the chat session.

---

## Configuration

The main parameters are defined in `app/config/config.py`:

| Variable             | Description                      | Default                            |
|----------------------|----------------------------------|------------------------------------|
| `GROQ_API_KEY`       | LLM API key (env var required)   | -                                  |
| `GROQ_MODEL_NAME`    | Groq or OpenAI model name        | `openai/gpt-oss-120b`              |
| `HF_TOKEN`           | Hugging Face API token (optional)| -                                  |
| `HUGGINGFACE_REPO_ID`| HuggingFace LLM repo             | `mistralai/Mistral-7B-Instruct-v0.3`|
| `DATA_PATH`          | PDF storage path                 | `data/`                            |
| `DB_FAISS_PATH`      | Vector DB path                   | `vectorstore/db_faiss`             |
| `CHUNK_SIZE`         | Doc chunking size (chars)        | 500                                |
| `CHUNK_OVERLAP`      | Doc chunk overlap (chars)        | 50                                 |

---

## Development

- Code is modularized for testability and scalability.
- Logging and custom exception handling in `app/common/`.
- LLM, PDF parsing, and retrieval logic can be extended for new models or data types.
- Includes a `Jenkinsfile` and a secondary `custom_jenkins/Dockerfile` for advanced CI/CD integration.

---

## Technologies Used

- **Python** (Flask, LangChain, PDF processing, FAISS)
- **LLMs:** Groq (Llama3), Hugging Face
- **Vector Storage:** FAISS
- **Docker** (containerization)
- **Jenkins** (optional CI/CD).

---

## License

[MIT](LICENSE) (if provided).

---

## Disclaimer

- This project uses LLMs and AI reasoning—always review decisions for compliance before production use.
- Sample policy files in `data/` are for demonstration only.
