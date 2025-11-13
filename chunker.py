from typing import List, Dict

class CodeChunker:
    """Chunks code files into smaller pieces for embedding."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at newline for cleaner chunks
            if end < len(text):
                last_newline = chunk.rfind('\n')
                if last_newline > self.chunk_size // 2:
                    chunk = chunk[:last_newline]
                    end = start + last_newline
            
            chunks.append(chunk)
            start = end - self.chunk_overlap
        
        return chunks
    
    def chunk_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Chunk all documents."""
        chunked_docs = []
        
        for doc in documents:
            content = doc['content']
            chunks = self.chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                chunked_docs.append({
                    'content': chunk,
                    'filepath': doc['filepath'],
                    'filename': doc['filename'],
                    'chunk_id': i,
                    'total_chunks': len(chunks)
                })
        
        return chunked_docs
