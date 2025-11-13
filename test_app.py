"""
Test script to verify the RAG system works
"""
import os
from dotenv import load_dotenv

def test_setup():
    """Test if everything is set up correctly."""
    print("Testing GitHub Codebase RAG Setup...")
    print("=" * 60)
    
    # Check .env file
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("   Run: python setup_env.py")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        return False
    
    print("✅ .env file exists")
    print(f"✅ GROQ_API_KEY found (length: {len(api_key)})")
    
    # Test imports
    try:
        from repo_loader import RepoLoader
        print("✅ repo_loader module imported")
        
        from chunker import CodeChunker
        print("✅ chunker module imported")
        
        from vector_store import VectorStore
        print("✅ vector_store module imported")
        
        from rag_engine import RAGEngine
        print("✅ rag_engine module imported")
        
        import streamlit
        print("✅ streamlit imported")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test Groq connection
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        print("✅ Groq client initialized")
        
        # Test API call
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            model="llama-3.3-70b-versatile",
            max_tokens=10
        )
        print("✅ Groq API test successful")
        
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return False
    
    print()
    print("=" * 60)
    print("🎉 All tests passed! You're ready to run the app.")
    print()
    print("Run the application with:")
    print("  streamlit run app.py")
    print()
    return True

if __name__ == "__main__":
    test_setup()
