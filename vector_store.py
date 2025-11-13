import faiss
import numpy as np
import pickle
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class VectorStore:
    """Manages embeddings and FAISS vector store."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Lazy import to avoid torch issues at startup
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        except Exception as e:
            #print(f"Warning: Could not load sentence-transformers: {e}")
            #print("Falling back to simple TF-IDF embeddings...")
            self.model = None
            self.dimension = 512
            self._init_tfidf()
        
        self.index = None
        self.documents = []
    
    def _init_tfidf(self):
        """Initialize simple TF-IDF vectorizer as fallback."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        
        self.TruncatedSVD = TruncatedSVD  # Store class for later use
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.svd = TruncatedSVD(n_components=self.dimension)
    
    def create_embeddings(self, chunks: List[Dict[str, str]]) -> np.ndarray:
        """Generate embeddings for text chunks."""
        texts = [chunk['content'] for chunk in chunks]
        
        if self.model is not None:
            # Use sentence-transformers
            embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        else:
            # Use TF-IDF fallback
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Adjust SVD components based on actual feature count
            n_features = tfidf_matrix.shape[1]
            n_components = min(self.dimension, n_features, len(texts))
            
            if n_components < self.dimension:
                print(f"Adjusting dimensions from {self.dimension} to {n_components} based on data size")
                self.dimension = n_components
                self.svd = self.TruncatedSVD(n_components=n_components)
            
            embeddings = self.svd.fit_transform(tfidf_matrix)
        
        return embeddings
    
    def build_index(self, chunks: List[Dict[str, str]]):
        """Build FAISS index from chunks."""
        print(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = self.create_embeddings(chunks)
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))
        
        # Store documents for retrieval
        self.documents = chunks
        
        print(f"Index built with {self.index.ntotal} vectors")
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Dict[str, str], float]]:
        """Search for top-k most similar chunks."""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        if self.model is not None:
            query_embedding = self.model.encode([query], convert_to_numpy=True)
        else:
            # Use TF-IDF fallback
            tfidf_query = self.vectorizer.transform([query])
            query_embedding = self.svd.transform(tfidf_query)
        
        # Search in FAISS
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Return documents with scores
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(distance)))
        
        return results
    
    def save(self, index_path: str = "faiss_index.bin", docs_path: str = "documents.pkl"):
        """Save index and documents to disk."""
        if self.index is not None:
            faiss.write_index(self.index, index_path)
            with open(docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
    
    def load(self, index_path: str = "faiss_index.bin", docs_path: str = "documents.pkl"):
        """Load index and documents from disk."""
        try:
            self.index = faiss.read_index(index_path)
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            return False
