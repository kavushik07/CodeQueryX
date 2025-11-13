# GitHub Codebase RAG System

A minimalistic RAG (Retrieval-Augmented Generation) system that allows you to ask questions about any GitHub repository.

## Features
- Clone any public GitHub repository
- Parse and chunk code files
- Generate embeddings using Sentence Transformers
- Store in FAISS vector database
- Answer questions using Groq's fast LLM API

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get a free Groq API key:
   - Visit https://console.groq.com/
   - Sign up for a free account
   - Create an API key

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_actual_key_here
```

## Run

```bash
streamlit run app.py
```

## Usage

1. Enter a GitHub repository URL (e.g., https://github.com/user/repo)
2. Click "Load Repository"
3. Wait for processing (cloning, chunking, embedding)
4. Ask questions about the codebase
5. Get AI-powered answers with relevant code context

## Tech Stack
- **Frontend**: Streamlit
- **LLM**: Groq (free, fast)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store**: FAISS
- **Repo Cloning**: GitPython
