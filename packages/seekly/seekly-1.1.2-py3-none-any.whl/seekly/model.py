"""
Model handling for Seekly CLI.
Provides functionality to load and use the codet5p-110m-embedding model.
"""

import torch # type: ignore
import numpy as np # type: ignore
import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModel, AutoConfig
from typing import List, Dict, Tuple

# Import constants from the seekly package
from seekly import DEFAULT_MODEL, DEFAULT_MAX_LENGTH

class EmbeddingModel:
    """Handles loading and inference of pre-trained model."""
    
    def __init__(self, model_name: str = DEFAULT_MODEL, verbose: bool = False):
        """
        Initialize the embedding model and tokenizer.
        
        Args:
            model_name: Hugging Face model identifier
            verbose: Whether to print detailed messages
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.config = None
        self.max_length = DEFAULT_MAX_LENGTH  # Use constant from config
        self.verbose = verbose
        
        # Create a directory to store cache for model
        self.cache_dir = os.path.join(str(Path.home()), ".seekly", "model_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Enable advanced embedding processing techniques
        self.enable_advanced_processing = True

    def load(self, verbose_override=None):
        """Load the model and tokenizer."""
        verbose = self.verbose if verbose_override is None else verbose_override
        try:
            # Added trust_remote_code=True to both tokenizer and model loading
            # Cache the model locally so it doesn't need to be downloaded every time
            if verbose:
                print(f"Loading model from {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir=self.cache_dir
            )
            self.config = AutoConfig.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir=self.cache_dir
            )
            self.model = AutoModel.from_pretrained(
                self.model_name,
                trust_remote_code=True, 
                config=self.config,
                cache_dir=self.cache_dir
            )
            self.model.to(self.device)
            self.model.eval()
            if verbose:
                print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def is_model_loaded(self):
        """Check if model is loaded."""
        return self.tokenizer is not None and self.model is not None
    
    def _normalize_code(self, text: str) -> str:
        """
        Normalize code to improve embedding quality by reducing noise.
        This is language-agnostic and focuses on structural patterns.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return text
            
        # Simple text-based normalization that works for all languages
        # These are structural patterns, not language-specific
        
        # Normalize whitespace (preserve indentation but standardize it)
        lines = text.split('\n')
        normalized_lines = []
        for line in lines:
            # Preserve leading whitespace (indentation)
            leading_space = len(line) - len(line.lstrip())
            if leading_space > 0:
                normalized = ' ' * leading_space + line.strip()
            else:
                normalized = line.strip()
            normalized_lines.append(normalized)
        
        # Remove redundant blank lines (more than 2 consecutive)
        result_lines = []
        blank_count = 0
        for line in normalized_lines:
            if not line:
                blank_count += 1
                if blank_count <= 2:  # Keep up to 2 consecutive blank lines
                    result_lines.append(line)
            else:
                blank_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _get_hierarchical_embeddings(self, text: str) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        Generate hierarchical embeddings that represent both fine-grained and
        broad context to improve semantic understanding.
        
        Args:
            text: Input text to embed hierarchically
            
        Returns:
            Tuple of (global_embedding, list_of_chunk_embeddings)
        """
        if not text or len(text) < 10:
            # For very short text, just create a single embedding
            embedding = self._generate_raw_embedding(text)
            return embedding, [embedding]
            
        # Create chunks based on structural boundaries
        chunks = self._create_semantic_chunks(text)
        
        # Generate embeddings for each chunk
        chunk_embeddings = []
        for chunk in chunks:
            try:
                chunk_embedding = self._generate_raw_embedding(chunk)
                chunk_embeddings.append(chunk_embedding)
            except Exception:
                # Skip problematic chunks
                continue
                
        # Generate global embedding from the full text
        global_embedding = self._generate_raw_embedding(text)
        
        return global_embedding, chunk_embeddings
    
    def _create_semantic_chunks(self, text: str) -> List[str]:
        """
        Create semantic chunks based on structural boundaries.
        This is language-agnostic and focuses on universal code patterns.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        # Use structural patterns to identify logical boundaries
        # These are universal patterns not tied to specific languages
        
        # First split by blank lines (most basic structural division)
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        # If the text is short enough to fit in one chunk, return it as is
        if len(text) <= self.max_length:
            return [text]
        
        # Process longer text into logical chunks
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # If adding this paragraph would exceed max size, store current chunk
            if len(current_chunk) + len(para) > self.max_length and current_chunk:
                chunks.append(current_chunk)
                current_chunk = para
            else:
                # Add separator if not the first paragraph in the chunk
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += para
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def _generate_raw_embedding(self, text: str) -> np.ndarray:
        """
        Generate a raw embedding using the pretrained model without additional processing.
        
        Args:
            text: Input text to embed
            
        Returns:
            Raw embedding vector
        """
        if not self.tokenizer or not self.model:
            raise ValueError("Model and tokenizer must be loaded before generating embeddings")
        
        try:
            # Standard tokenization
            inputs = self.tokenizer(text, return_tensors="pt", 
                                   padding=True, truncation=True, 
                                   max_length=self.max_length)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embedding
            with torch.no_grad():
                outputs = self.model(**inputs)
                
                # Handle different output formats from the model
                if isinstance(outputs, torch.Tensor):
                    embeddings = outputs.mean(dim=1)
                elif hasattr(outputs, 'last_hidden_state'):
                    embeddings = outputs.last_hidden_state.mean(dim=1)
                else:
                    embeddings = outputs[0].mean(dim=1)
            
            return embeddings.cpu().numpy()[0]
        except Exception as e:
            if self.verbose:
                print(f"Error generating raw embedding: {str(e)}")
            raise
    
    def _apply_pooling_strategy(self, embeddings: List[np.ndarray]) -> np.ndarray:
        """
        Apply advanced pooling strategy to combine multiple embeddings.
        This produces more stable vector representations.
        
        Args:
            embeddings: List of embedding vectors to combine
            
        Returns:
            Combined embedding vector
        """
        if not embeddings:
            return np.zeros(self.model.config.hidden_size)
            
        if len(embeddings) == 1:
            return embeddings[0]
            
        # Convert to numpy array for efficient operations
        embeddings_array = np.stack(embeddings)
        
        # Use weighted pooling (attention-like mechanism)
        # Calculate the magnitude of each embedding as a measure of information content
        magnitudes = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        # Softmax-like normalization of magnitudes
        weights = magnitudes / np.sum(magnitudes)
        
        # Apply weighted pooling
        pooled_embedding = np.sum(embeddings_array * weights, axis=0)
        
        # Normalize the result
        norm = np.linalg.norm(pooled_embedding)
        if norm > 0:
            pooled_embedding = pooled_embedding / norm
            
        return pooled_embedding

    def _apply_structural_analysis(self, text: str) -> Dict[str, float]:
        """
        Analyze structural properties of code to improve embedding quality.
        This is language-agnostic and focuses on universal code patterns.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary of structural properties
        """
        # These are general structural properties that apply to all programming languages
        properties = {
            'line_count': 0,
            'indent_levels': 0,
            'bracket_balance': 0,
            'character_density': 0.0,
        }
        
        if not text:
            return properties
            
        lines = text.split('\n')
        properties['line_count'] = len(lines)
        
        # Calculate indentation (a proxy for code structure)
        indent_levels = set()
        for line in lines:
            if line.strip():  # Skip empty lines
                # Count leading spaces/tabs
                indent = len(line) - len(line.lstrip())
                indent_levels.add(indent)
        properties['indent_levels'] = len(indent_levels)
        
        # Calculate bracket balance and density
        opening_brackets = sum(text.count(c) for c in '({[')
        closing_brackets = sum(text.count(c) for c in ')}]')
        properties['bracket_balance'] = min(opening_brackets, closing_brackets) / max(1, max(opening_brackets, closing_brackets))
        
        # Character density (non-whitespace to total)
        total_chars = len(text)
        non_whitespace = sum(1 for c in text if not c.isspace())
        properties['character_density'] = non_whitespace / max(1, total_chars)
        
        return properties

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate enhanced semantic embedding using multiple advanced techniques.
        
        Args:
            text: Input text to embed
            
        Returns:
            Enhanced embedding vector
        """
        if not self.tokenizer or not self.model:
            raise ValueError("Model and tokenizer must be loaded before generating embeddings")
        
        try:
            if not self.enable_advanced_processing or not text or len(text) < 10:
                # Fall back to basic embedding for very short text or if advanced processing is disabled
                return self._generate_raw_embedding(text)
            
            # Step 1: Normalize code to reduce noise
            normalized_text = self._normalize_code(text)
            
            # Step 2: Generate hierarchical embeddings
            global_embedding, chunk_embeddings = self._get_hierarchical_embeddings(normalized_text)
            
            # Step 3: Apply advanced pooling strategy
            if chunk_embeddings:
                # Include global embedding in pooling
                all_embeddings = [global_embedding] + chunk_embeddings
                pooled_embedding = self._apply_pooling_strategy(all_embeddings)
            else:
                pooled_embedding = global_embedding
            
            # Normalize the final embedding
            norm = np.linalg.norm(pooled_embedding)
            if norm > 0:
                pooled_embedding = pooled_embedding / norm
                
            return pooled_embedding
            
        except Exception as e:
            if self.verbose:
                print(f"Error generating enhanced embedding: {str(e)}")
            # Fall back to basic embedding for robustness
            try:
                return self._generate_raw_embedding(text)
            except:
                # If everything fails, return a zero vector
                return np.zeros(self.model.config.hidden_size)

    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a batch of texts with enhanced processing.
        
        Args:
            texts: List of input texts
            
        Returns:
            Numpy array of embeddings, shape (len(texts), embedding_dim)
        """
        if not self.tokenizer or not self.model:
            raise ValueError("Model and tokenizer must be loaded before generating embeddings")
        
        embeddings = []
        for text in texts:
            try:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                if self.verbose:
                    print(f"Error generating embedding for text in batch: {str(e)}")
                # Add a zero vector for failed embeddings to maintain batch size
                embeddings.append(np.zeros(self.model.config.hidden_size))
        
        return np.stack(embeddings)

    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (float between -1 and 1)
        """
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        # Prevent division by zero
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return np.dot(embedding1, embedding2) / (norm1 * norm2)