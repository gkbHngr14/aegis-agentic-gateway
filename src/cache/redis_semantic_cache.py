# ---------------------------------------------------------------------------
# 3. REDISVL SEMANTIC CACHE WITH XFETCH STAMPEDE PROTECTION
# ---------------------------------------------------------------------------
import math
import time
import random
import logging
from typing import Dict, List, Any, Optional  # <--- Added typing imports

logger = logging.getLogger("AegisCacheEngine")

class RedisVLSemanticCache:
    """
    Semantic Vector Cache powered by RedisVL.
    Uses Cosine Similarity (>= 0.94) and XFetch Probabilistic Early Expiration.
    """
    
    def __init__(self, similarity_threshold: float = 0.94, beta: float = 1.0):
        self.similarity_threshold = similarity_threshold
        self.beta = beta  # XFetch aggressiveness multiplier
        # Simulated In-Memory Redis Hash Vector Store
        self._cache_store: Dict[str, Dict[str, Any]] = {}

    def _generate_query_embedding(self, text: str) -> List[float]:
        """Simulates local 384-dim MiniLM vector embedding (<5ms)."""
        random.seed(hash(text))
        return [random.uniform(-1.0, 1.0) for _ in range(384)]

    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculates cosine similarity between two 384-dim embeddings."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0

    def get(self, query_text: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Executes KNN search over cached prompt vectors for tenant_id.
        Applies XFetch algorithm: Read if random() > exp(-delta / (beta * ttl)).
        """
        query_vec = self._generate_query_embedding(query_text)
        now = time.time()

        for cache_key, entry in self._cache_store.items():
            # Tenant Security Boundary check at Cache Layer
            if entry["tenant_id"] != tenant_id:
                continue

            similarity = self._calculate_cosine_similarity(query_vec, entry["embedding"])
            
            if similarity >= self.similarity_threshold:
                # Calculate XFetch Probabilistic Early Expiration
                ttl_remaining = entry["expire_timestamp"] - now
                delta = entry["compute_time_ms"] / 1000.0  # Time taken to compute original RAG answer
                
                # XFetch Formula: -beta * delta * ln(random())
                xfetch_value = -self.beta * delta * math.log(random.uniform(0.0001, 1.0))
                
                if xfetch_value > ttl_remaining:
                    logger.info(f"[XFetch Triggered] Probabilistic early expiration for key '{cache_key}'. Refreshing asynchronously.")
                    return None  # Treat as probabilistic cache miss to trigger background refresh
                
                logger.info(f"[RedisVL Hit] Semantic Match found (Similarity: {similarity:.4f} >= {self.similarity_threshold})")
                return entry["payload"]

        return None

    def set(self, query_text: str, tenant_id: str, payload: Dict[str, Any], compute_time_ms: float, ttl_seconds: float = 86400):
        """Stores query embedding and response payload in RedisVL cache."""
        cache_key = f"cache:{tenant_id}:{hash(query_text)}"
        self._cache_store[cache_key] = {
            "tenant_id": tenant_id,
            "embedding": self._generate_query_embedding(query_text),
            "payload": payload,
            "compute_time_ms": compute_time_ms,
            "expire_timestamp": time.time() + ttl_seconds
        }
        logger.info(f"[RedisVL Cached] Successfully cached response for key '{cache_key}' (TTL: {ttl_seconds}s)")