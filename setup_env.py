"""
Setup script to create .env file with Groq API key
"""
import os

def setup_env():
    print("=" * 60)
    print("GitHub Codebase RAG - Environment Setup")
    print("=" * 60)
    print()
    print("You need a FREE Groq API key to use this application.")
    print()
    print("Steps to get your API key:")
    print("1. Visit: https://console.groq.com/")
    print("2. Sign up for a free account (no credit card required)")
    print("3. Go to 'API Keys' section")
    print("4. Create a new API key")
    print("5. Copy the key")
    print()
    
    api_key = input("Enter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return
    
    # Create .env file
    with open(".env", "w") as f:
        f.write(f"GROQ_API_KEY={api_key}\n")
    
    print()
    print("✅ .env file created successfully!")
    print()
    print("You can now run the application with:")
    print("  streamlit run app.py")
    print()

if __name__ == "__main__":
    setup_env()
