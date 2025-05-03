"""
Advanced semantic search architecture for Seekly CLI.
Implements multi-view query expansion, vector search and reranking.
"""


import numpy as np # type: ignore
from typing import List, Tuple, Any
import re
import torch # type: ignore
from sentence_transformers import SentenceTransformer, util # type: ignore

from seekly.model import EmbeddingModel
from seekly.file_processor import (
    list_files, FileProcessor
)
# Import the DEFAULT_MODEL from seekly.__init__ 
from seekly import DEFAULT_MODEL


# Define SearchResult class to store search results
class SearchResult:
    """
    Represents a search result with file path, similarity score, and content type.
    """
    def __init__(self, file_path: str, similarity: float, content_type: str = "file"):
        self.file_path = file_path
        self.similarity = similarity
        self.content_type = content_type

    def __repr__(self) -> str:
        return f"SearchResult(file_path='{self.file_path}', similarity={self.similarity:.4f}, content_type='{self.content_type}')"


# Efficient vector similarity functions for semantic search
def cosine_similarity_fn(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity (float between -1 and 1)
    """
    # Ensure both are normalized
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    
    # Avoid division by zero
    if a_norm == 0 or b_norm == 0:
        return 0.0
        
    # Calculate cosine similarity
    return np.dot(a, b) / (a_norm * b_norm)


class SeeklySearch:
    def __init__(self, model_name: str = None, verbose: bool = False):
        # Use DEFAULT_MODEL from __init__.py if model_name is not provided
        self.model_name = model_name if model_name else DEFAULT_MODEL
        self.verbose = verbose
        self._model_loaded = False
        self.model = None
        
    def search(self, query: str, directory: str, top_k: int = 5, threshold: float = 0.3, force_reindex: bool = False) -> List[Tuple[str, float]]:
        """
        Perform semantic search with improved code understanding.
        """
        if not self.is_model_loaded():
            self.load_model(verbose_override=self.verbose)
            
        # Enhance query with code-specific context
        enhanced_query = self._enhance_query(query)
        query_embedding = self.model.encode(enhanced_query, convert_to_tensor=True)
        
        # Process and index files
        embeddings = []
        file_contents = []
        
        for file_path in self._get_code_files(directory):
            content, functions = self.file_processor.process_file(file_path)
            if not content:
                continue
                
            # Generate embeddings for both whole file and function-level chunks
            file_embedding = self.model.encode(content, convert_to_tensor=True)
            embeddings.append((file_path, file_embedding, "file"))
            
            # Add function-level granularity
            for func_name, func_content in functions:
                func_embedding = self.model.encode(func_content, convert_to_tensor=True)
                embeddings.append((file_path, func_embedding, f"function:{func_name}"))
            
            file_contents.append((file_path, content))
        
        # Calculate similarities with adjusted weights
        results = []
        for file_path, embedding, content_type in embeddings:
            similarity = self._calculate_similarity(query_embedding, embedding)
            
            # Adjust similarity based on content type and query context
            adjusted_similarity = self._adjust_similarity(
                similarity,
                content_type,
                query,
                next(content for path, content in file_contents if path == file_path)
            )
            
            results.append(SearchResult(
                file_path=file_path,
                similarity=adjusted_similarity,
                content_type=content_type
            ))
        
        # Sort and filter results
        unique_results = self._deduplicate_results(results)
        sorted_results = sorted(unique_results, key=lambda x: x.similarity, reverse=True)
        
        # Filter by threshold and return as tuples of (path, score)
        filtered_results = [(r.file_path, r.similarity) for r in sorted_results if r.similarity >= threshold]
        return filtered_results[:top_k]

    def is_model_loaded(self) -> bool:
        """Check if the model is already loaded"""
        return self._model_loaded and self.model is not None
        
    def load_model(self, verbose_override: bool = None) -> bool:
        """Load the embedding model, return success status"""
        verbose = self.verbose if verbose_override is None else verbose_override
        try:
            if verbose:
                print(f"[DEBUG] Loading model: {self.model_name}")
            
            self.model = SentenceTransformer(self.model_name)
            self.file_processor = FileProcessor()
            self._model_loaded = True
            
            if verbose:
                print(f"[DEBUG] Model loaded successfully: {self.model_name}")
                # Print some model characteristics to verify it's the right one
                print(f"[DEBUG] Model size: {sum(p.numel() for p in self.model.parameters())} parameters")
                print(f"[DEBUG] Model embedding dimensions: {self.model.get_sentence_embedding_dimension()}")
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load model {self.model_name}: {str(e)}")
            self._model_loaded = False
            return False

    def _enhance_query(self, query: str) -> str:
        """
        Enhance the search query with code-specific context.
        """
        # Add code-specific context markers
        code_indicators = {
            'check': 'function:check',
            'program': 'code:',
            'function': 'function:',
            'implementation': 'code:',
        }
        
        enhanced = query
        for indicator, marker in code_indicators.items():
            if indicator in query.lower():
                enhanced = f"{marker} {enhanced}"
                break
        
        return enhanced

    def _calculate_similarity(self, query_embedding: torch.Tensor, doc_embedding: torch.Tensor) -> float:
        """
        Calculate semantic similarity with improved normalization.
        """
        similarity = util.pytorch_cos_sim(query_embedding, doc_embedding)[0][0]
        return float(similarity)

    def _adjust_similarity(self, base_similarity: float, content_type: str, query: str, content: str) -> float:
        """
        Adjust similarity scores based on content type and context.
        """
        # Base score
        score = base_similarity
        
        # Boost for exact function matches
        if content_type.startswith("function:"):
            func_name = content_type.split(":")[1]
            query_terms = query.lower().split()
            if any(term in func_name.lower() for term in query_terms):
                score *= 1.2
        
        # Boost for relevant code patterns
        if self._has_relevant_code_patterns(query, content):
            score *= 1.15
            
        return min(score, 1.0)  # Normalize to [0, 1]

    def _has_relevant_code_patterns(self, query: str, content: str) -> bool:
        """
        Check if content contains patterns relevant to the query.
        """
        query_patterns = {
            'check': r'\b(check|is|verify)\w*\b',
            'calculate': r'\b(calculate|compute)\w*\b',
            'find': r'\b(find|search|lookup)\w*\b',
        }
        
        query_lower = query.lower()
        for key, pattern in query_patterns.items():
            if key in query_lower and re.search(pattern, content, re.IGNORECASE):
                return True
                
        return False

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Remove duplicate results while keeping the highest similarity score.
        """
        seen_files = {}
        for result in results:
            if result.file_path not in seen_files or result.similarity > seen_files[result.file_path].similarity:
                seen_files[result.file_path] = result
        
        return list(seen_files.values())
        
    def _get_code_files(self, directory: str) -> List[str]:
        """
        Get all code files in the given directory.
        
        Args:
            directory: Directory to scan for code files
            
        Returns:
            List of file paths
        """
        return list_files(directory)