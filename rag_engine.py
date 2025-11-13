import os
from typing import List, Dict, Tuple
from groq import Groq
from dotenv import load_dotenv
import tiktoken

class RAGEngine:
    """Handles RAG pipeline with Groq LLM."""
    
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Fast and capable model
        
        # Context limits for the model (very conservative for Groq limits)
        self.max_context_tokens = 10000  
        self.max_response_tokens = 1024
        
        # Initialize tokenizer for counting tokens
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Use compatible tokenizer
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Fallback
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the tokenizer."""
        try:
            return len(self.tokenizer.encode(text))
        except:
            # Fallback: rough estimate of 4 characters per token
            return len(text) // 4
    
    def select_chunks_within_limit(self, retrieved_chunks: List[Tuple], query: str) -> List[Dict[str, str]]:
        """Select maximum number of chunks that fit within context limit."""
        # Base prompt template tokens (approximate)
        base_prompt = f"""You are a helpful code assistant. Answer the user's question based on the provided code context.

Context from the codebase:

User Question: {query}

Instructions:
- Answer based on the provided code context
- Be specific and reference file names when relevant
- If the context doesn't contain enough information, say so
- Provide code examples if helpful
- Be concise but thorough
- If asked to summarise what the project does,explain what the project does,you do not need to cite code examples for that

Answer:"""
        
        base_tokens = self.count_tokens(base_prompt)
        available_tokens = self.max_context_tokens - base_tokens - 200  # Larger buffer for safety
        
        selected_chunks = []
        current_tokens = 0
        
        # Sort chunks by relevance (lower distance = more relevant)
        sorted_chunks = sorted(retrieved_chunks, key=lambda x: x[1])
        
        for i, (doc, score) in enumerate(sorted_chunks):
            # Create chunk text as it would appear in prompt
            filepath = doc.get('filepath', 'unknown')
            content = doc.get('content', '')
            chunk_text = f"\n--- Code Snippet {len(selected_chunks) + 1} from {filepath} ---\n{content}\n"
            
            chunk_tokens = self.count_tokens(chunk_text)
            
            # Check if adding this chunk would exceed limit
            if current_tokens + chunk_tokens <= available_tokens:
                selected_chunks.append(doc)
                current_tokens += chunk_tokens
            else:
                # Try to fit a truncated version if it's the first chunk and we have space
                if len(selected_chunks) == 0 and available_tokens > 200:
                    # Truncate content to fit
                    header_text = f"\n--- Code Snippet 1 from {filepath} ---\n\n"
                    header_tokens = self.count_tokens(header_text)
                    max_content_tokens = available_tokens - header_tokens
                    
                    if max_content_tokens > 50:  # Minimum useful content
                        # Estimate characters needed (rough: 4 chars per token)
                        max_chars = max_content_tokens * 3  # More conservative estimate
                        truncated_content = content[:max_chars] + "..." if len(content) > max_chars else content
                        
                        truncated_doc = doc.copy()
                        truncated_doc['content'] = truncated_content
                        selected_chunks.append(truncated_doc)
                break
        
        return selected_chunks
    
    def create_prompt(self, query: str, context_chunks: List[Dict[str, str]]) -> str:
        """Create RAG prompt with retrieved context."""
        context_text = ""
        
        for i, chunk in enumerate(context_chunks, 1):
            filepath = chunk.get('filepath', 'unknown')
            content = chunk.get('content', '')
            context_text += f"\n--- Code Snippet {i} from {filepath} ---\n{content}\n"
        
        prompt = f"""You are a helpful code assistant. Answer the user's question based on the provided code context.

Context from the codebase:
{context_text}

User Question: {query}

Instructions:
- Answer based on the provided code context
- Be specific and reference file names when relevant
- If the context doesn't contain enough information, say so
- Provide code examples if helpful
- Be concise but thorough
- If asked to summarise what the project does,explain what the project does,you do not need to cite code examples for that

Answer:"""
        
        # Final validation of prompt size
        prompt_tokens = self.count_tokens(prompt)
        
        if prompt_tokens > self.max_context_tokens:
            # This shouldn't happen with proper chunk selection, but just in case
            raise ValueError(f"Prompt exceeds token limit: {prompt_tokens} > {self.max_context_tokens}")
        
        return prompt
    
    def generate_answer(self, query: str, context_chunks: List[Dict[str, str]]) -> str:
        """Generate answer using Groq LLM."""
        try:
            prompt = self.create_prompt(query, context_chunks)
            
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1024,
            )
            
            answer = chat_completion.choices[0].message.content
            return answer
        
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def answer_question(self, query: str, retrieved_chunks: List[tuple]) -> Dict[str, any]:
        """Answer question with retrieved context, automatically selecting optimal chunks."""
        # Select chunks that fit within context limits
        context_chunks = self.select_chunks_within_limit(retrieved_chunks, query)
        
        # Generate answer
        answer = self.generate_answer(query, context_chunks)
        
        # Prepare response with sources (only from selected chunks)
        sources = []
        selected_filepaths = {chunk.get('filepath', 'unknown') for chunk in context_chunks}
        
        for doc, score in retrieved_chunks:
            filepath = doc.get('filepath', 'unknown')
            if filepath in selected_filepaths:
                sources.append({
                    'filepath': filepath,
                    'score': score,
                    'preview': doc.get('content', '')[:200] + '...'
                })
        
        # Add metadata about chunk selection
        total_retrieved = len(retrieved_chunks)
        total_used = len(context_chunks)
        
        if total_used < total_retrieved:
            answer += ""#f"\n\n*Note: Used {total_used} of {total_retrieved} retrieved chunks to stay within context limits.*"
        
        return {
            'answer': answer,
            'sources': sources,
            'chunks_used': total_used,
            'chunks_retrieved': total_retrieved
        }
