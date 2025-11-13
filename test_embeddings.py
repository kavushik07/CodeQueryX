#!/usr/bin/env python3
"""
Test script to verify sentence-transformers is working correctly
"""

def test_sentence_transformers():
    """Test if sentence-transformers can load and create embeddings."""
    try:
        print("Testing sentence-transformers...")
        
        # Try to import sentence-transformers
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers imported successfully")
        
        # Try to load a model
        print("Loading model 'all-MiniLM-L6-v2'...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded successfully")
        
        # Try to create embeddings
        test_texts = ["This is a test sentence", "Another test sentence"]
        print("Creating embeddings...")
        embeddings = model.encode(test_texts, convert_to_numpy=True)
        print(f"✅ Embeddings created successfully: shape {embeddings.shape}")
        
        print("\n🎉 All tests passed! sentence-transformers is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_sentence_transformers()
