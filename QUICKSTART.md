# 🚀 Quick Start Guide

## Step 1: Get Your Free Groq API Key (2 minutes)

1. Open https://console.groq.com/ in your browser
2. Click "Sign Up" (it's FREE, no credit card needed)
3. After signing in, click "API Keys" in the left sidebar
4. Click "Create API Key"
5. Copy the key (starts with "gsk_...")

## Step 2: Set Up Environment

Run the setup script:
```bash
python setup_env.py
```

Paste your API key when prompted.

## Step 3: Test Everything Works

```bash
python test_app.py
```

If all tests pass, you're ready!

## Step 4: Run the Application

```bash
streamlit run app.py
```

The app will open automatically in your browser at http://localhost:8501

## Step 5: Use the App

1. Enter a GitHub URL (e.g., `https://github.com/psf/requests`)
2. Click "Load Repository"
3. Wait for processing (1-2 minutes for small repos)
4. Ask questions like:
   - "What does the main file do?"
   - "How does error handling work?"
   - "Explain the authentication flow"
   - "What dependencies are used?"

## Troubleshooting

### "GROQ_API_KEY not found"
- Make sure you ran `python setup_env.py`
- Check that `.env` file exists in the project folder
- Verify the API key is correct

### "Module not found" errors
- Run: `pip install -r requirements.txt`

### Repo loading is slow
- Normal for large repos (>100 files)
- First time downloads embedding model (~100MB)
- Subsequent runs are faster

## Example Repositories to Try

- https://github.com/pallets/flask (web framework)
- https://github.com/psf/requests (HTTP library)
- https://github.com/fastapi/fastapi (API framework)
- Any of your own public repos!

## Tips

- Smaller repos (<50 files) work best for testing
- Questions should be specific to the codebase
- The AI uses actual code context to answer
- Check the "ces" to see which files were used
