# Setup Guide

## Get Your Free Groq API Key

1. Visit: https://console.groq.com/
2. Sign up for a free account (no credit card required)
3. Go to API Keys section
4. Create a new API key
5. Copy the key

## Create .env File

Create a file named `.env` in the project root with:

```
GROQ_API_KEY=your_actual_groq_api_key_here
```

Replace `your_actual_groq_api_key_here` with your actual key from Groq.

## Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at http://localhost:8501
