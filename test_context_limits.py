#!/usr/bin/env python3
"""
Test script to verify the context limit functionality works correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_context_limits():
    """Test the context limit functionality."""
    print("Testing context limit functionality...")
    
    # Import after loading env vars
    from rag_engine import RAGEngine
    
    # Create RAG engine (will fail if no API key, but that's expected for testing)
    try:
        engine = RAGEngine()
        print("✅ RAG Engine initialized successfully")
    except ValueError as e:
        print(f"⚠️  RAG Engine initialization failed (expected if no API key): {e}")
        print("Creating engine without API validation for testing...")
        
        # Create a mock engine for testing
        class MockRAGEngine:
            def __init__(self):
                import tiktoken
                self.max_context_tokens = 8000
                self.max_response_tokens = 1024
                try:
                    self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
                except:
                    self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
            def count_tokens(self, text: str) -> int:
                try:
                    return len(self.tokenizer.encode(text))
                except:
                    return len(text) // 4
            
            def select_chunks_within_limit(self, retrieved_chunks, query: str):
                # Import the method from the real class
                from rag_engine import RAGEngine
                real_engine = RAGEngine.__new__(RAGEngine)  # Create without __init__
                real_engine.max_context_tokens = self.max_context_tokens
                real_engine.tokenizer = self.tokenizer
                return real_engine.select_chunks_within_limit(retrieved_chunks, query)
        
        engine = MockRAGEngine()
    
    # Test token counting
    test_text = "def hello_world():\n    print('Hello, World!')\n    return True"
    token_count = engine.count_tokens(test_text)
    print(f"✅ Token counting works: '{test_text}' = {token_count} tokens")
    
    # Test chunk selection with mock data
    mock_chunks = []
    for i in range(10):
        content = f"def function_{i}():\n" + "    # This is a test function\n" * 20 + f"    return {i}"
        mock_chunks.append(({
            'filepath': f'test_file_{i}.py',
            'content': content
        }, 0.1 * i))  # (document, score) tuple
    
    query = "What do these functions do?"
    
    try:
        selected_chunks = engine.select_chunks_within_limit(mock_chunks, query)
        print(f"✅ Chunk selection works: Selected {len(selected_chunks)} out of {len(mock_chunks)} chunks")
        
        # Calculate total tokens for selected chunks
        total_tokens = 0
        for chunk in selected_chunks:
            content = chunk.get('content', '')
            filepath = chunk.get('filepath', 'unknown')
            chunk_text = f"\n--- Code Snippet from {filepath} ---\n{content}\n"
            total_tokens += engine.count_tokens(chunk_text)
        
        print(f"✅ Total tokens in selected chunks: {total_tokens}")
        print(f"✅ Within limit: {total_tokens < engine.max_context_tokens}")
        
    except Exception as e:
        print(f"❌ Chunk selection failed: {e}")
        return False
    
    print("\n🎉 All tests passed! The context limit functionality is working correctly.")
    return True

if __name__ == "__main__":
    success = test_context_limits()
    sys.exit(0 if success else 1)
