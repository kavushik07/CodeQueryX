import streamlit as st
import os
from pathlib import Path
from repo_loader import RepoLoader
from chunker import CodeChunker
from vector_store import VectorStore
from rag_engine import RAGEngine

# Page config
st.set_page_config(
    page_title="GitHub Codebase RAG",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None
if 'repo_loaded' not in st.session_state:
    st.session_state.repo_loaded = False
if 'repo_name' not in st.session_state:
    st.session_state.repo_name = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Title and description
st.title("🔍 CodeQuery")
st.markdown("Ask questions about any GitHub repository using AI-powered search")

# Sidebar for repo loading
with st.sidebar:
    st.header("📦 Load Repository")
    
    # Retrieval information
    #st.subheader("⚙️ Retrieval Settings")
    #st.info("🤖 **Smart Context Management**: The system automatically retrieves the maximum number of relevant code chunks that fit within the API's context limits, ensuring optimal performance without manual tuning.")
    
    st.divider()
    
    # # Check for API key
    # if not os.getenv("GROQ_API_KEY"):
    #     st.error("⚠️ GROQ_API_KEY not found!")
    #     st.info("Please create a `.env` file with your Groq API key")
    #     st.code("GROQ_API_KEY=your_key_here")
    #     st.stop()
    
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/user/repo"
    )
    
    load_button = st.button("🚀 Load Repository", type="primary", use_container_width=True)
    
    if load_button and repo_url:
        try:
            with st.spinner("Cloning repository..."):
                loader = RepoLoader()
                documents = loader.load_repo(repo_url)
                
                if not documents:
                    st.error("No code files found in repository")
                    st.stop()
                
                st.success(f"✅ Found {len(documents)} files")
            
            with st.spinner("Chunking documents..."):
                chunker = CodeChunker(chunk_size=3000, chunk_overlap=200)
                chunks = chunker.chunk_documents(documents)
                st.success(f"✅ Created {len(chunks)} chunks")
            
            with st.spinner("Generating embeddings and building index..."):
                vector_store = VectorStore()
                vector_store.build_index(chunks)
                st.session_state.vector_store = vector_store
                st.success(f"✅ Index built with {len(chunks)} vectors")
            
            with st.spinner("Initializing RAG engine..."):
                rag_engine = RAGEngine()
                st.session_state.rag_engine = rag_engine
                st.success("✅ RAG engine ready")
            
            st.session_state.repo_loaded = True
            st.session_state.repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            st.session_state.chat_history = []
            
            st.balloons()
            
        except Exception as e:
            st.error(f"Error loading repository: {str(e)}")
            st.exception(e)
    
    # Show repo status
    if st.session_state.repo_loaded:
        st.divider()
        st.success(f"✅ Repository loaded: **{st.session_state.repo_name}**")
        
        if st.button("🔄 Load New Repository", use_container_width=True):
            st.session_state.repo_loaded = False
            st.session_state.vector_store = None
            st.session_state.rag_engine = None
            st.session_state.chat_history = []
            st.rerun()

# Main chat interface
if not st.session_state.repo_loaded:
    st.info("👈 Enter a GitHub repository URL in the sidebar to get started")
    
    # Example queries
    st.markdown("### 💡 Example Questions You Can Ask:")
    st.markdown("""
    - What does the main.py file do?
    - How does the API endpoint handle errors?
    - Explain the authentication flow
    - What database is being used?
    - Show me the configuration setup
    - How are tests structured?
    """)
    
else:
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and "sources" in message:
                chunks_used = message.get('chunks_used', len(message["sources"]))
                chunks_retrieved = message.get('chunks_retrieved', len(message["sources"]))
                with st.expander(f"📚 View Sources ({chunks_used} chunks used from {chunks_retrieved} retrieved)"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**{i}. {source['filepath']}** (relevance score: {source['score']:.2f})")
                        st.code(source['preview'], language="python")
    
    # Chat input
    query = st.chat_input("Ask a question about the codebase...")
    
    if query:
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        with st.chat_message("user"):
            st.markdown(query)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching codebase..."):
                # Retrieve a reasonable number of chunks (let RAG engine select optimal subset)
                max_chunks = min(30, st.session_state.vector_store.index.ntotal if st.session_state.vector_store.index else 20)
                retrieved_chunks = st.session_state.vector_store.search(query, k=max_chunks)
                
                if not retrieved_chunks:
                    response = "I couldn't find relevant information in the codebase."
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                else:
                    # Generate answer
                    with st.spinner("Generating answer..."):
                        result = st.session_state.rag_engine.answer_question(query, retrieved_chunks)
                        
                        answer = result['answer']
                        sources = result['sources']
                        chunks_used = result.get('chunks_used', len(sources))
                        chunks_retrieved = result.get('chunks_retrieved', len(sources))
                        
                        st.markdown(answer)
                        
                        # Show sources with context info
                        with st.expander(f"📚 View Sources ({chunks_used} chunks used from {chunks_retrieved} retrieved)"):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"**{i}. {source['filepath']}** (relevance score: {source['score']:.2f})")
                                st.code(source['preview'], language="python")
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                            "chunks_used": chunks_used,
                            "chunks_retrieved": chunks_retrieved
                        })

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
   
</div>
""", unsafe_allow_html=True)
