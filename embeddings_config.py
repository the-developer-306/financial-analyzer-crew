"""
Embeddings configuration for CrewAI using Sentence Transformers from HuggingFace
"""
import os
from dotenv import load_dotenv

load_dotenv()

def configure_embeddings():
    """
    Configure embeddings to use Sentence Transformers from HuggingFace
    This is used by ChromaDB which CrewAI uses internally for embeddings
    """
    from chromadb.utils import embedding_functions
    
    # Get embeddings model from environment or use default
    embeddings_model = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Create sentence transformer embedding function
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embeddings_model
    )
    
    return sentence_transformer_ef

# Pre-configure embeddings on module import
try:
    embedding_function = configure_embeddings()
    print(f"✓ Embeddings configured with: {os.getenv('EMBEDDINGS_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')}")
except Exception as e:
    print(f"⚠ Warning: Could not configure embeddings: {e}")
    embedding_function = None
