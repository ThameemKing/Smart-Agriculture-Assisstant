"""Knowledge base management for farming information"""

import logging
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Manage farming knowledge base and similarity search"""
    
    def __init__(self, config):
        """Initialize Knowledge Base
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.kb_dir = Path(config.get('kb_dir', 'data/knowledge_base'))
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        
        self.documents = []
        self.vectorizer = TfidfVectorizer(lowercase=True, 
                                          stop_words='english',
                                          max_features=5000)
        self.tfidf_matrix = None
        
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load knowledge base from files"""
        try:
            logger.info("Loading knowledge base...")
            
            # Load from JSON file
            kb_file = self.kb_dir / 'farming_knowledge.json'
            if kb_file.exists():
                with open(kb_file, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)
                    self.documents = kb_data.get('documents', [])
                    logger.info(f"Loaded {len(self.documents)} documents")
            else:
                logger.warning(f"Knowledge base file not found: {kb_file}")
                self.load_default_knowledge_base()
            
            # Build TF-IDF matrix
            if self.documents:
                doc_texts = [doc.get('content', '') for doc in self.documents]
                self.tfidf_matrix = self.vectorizer.fit_transform(doc_texts)
                logger.info(f"TF-IDF matrix built: {self.tfidf_matrix.shape}")
                
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.load_default_knowledge_base()
    
    def load_default_knowledge_base(self):
        """Load default farming knowledge"""
        self.documents = [
            {
                "id": 1,
                "topic": "Tomato Diseases",
                "content": "Tomato leaves turning yellow can be due to nitrogen deficiency, yellowing virus, or poor drainage. Apply balanced fertilizer, ensure proper drainage, and remove infected leaves. Use organic fungicide if needed.",
                "keywords": ["tomato", "yellow", "leaves", "disease", "nutrient"]
            },
            {
                "id": 2,
                "topic": "Rice Fertilizer",
                "content": "Rice requires NPK fertilizer in 2:1:1 ratio. Apply nitrogen in three splits: 25% at planting, 50% at tillering, 25% at panicle initiation. Urea is commonly used source of nitrogen.",
                "keywords": ["rice", "fertilizer", "nitrogen", "NPK"]
            },
            {
                "id": 3,
                "topic": "Cotton Pest Control",
                "content": "Common cotton pests: bollworms, aphids, spider mites. Use integrated pest management: scout fields regularly, use pheromone traps, apply neem oil spray, use selective pesticides if threshold exceeded.",
                "keywords": ["cotton", "pests", "control", "bollworm", "aphid"]
            },
            {
                "id": 4,
                "topic": "Water Conservation",
                "content": "Save water using drip irrigation, mulching, and crop rotation. Drip irrigation reduces water by 50-60%. Mulch reduces evaporation. Grow water-efficient crops during dry season.",
                "keywords": ["water", "conservation", "irrigation", "drip"]
            },
            {
                "id": 5,
                "topic": "Wheat Sowing",
                "content": "Optimal wheat sowing time: October-November in India. Soil temperature should be 15-20°C. Use certified seeds at 100-125 kg/hectare. Ensure proper soil preparation and drainage.",
                "keywords": ["wheat", "sowing", "season", "time", "seeds"]
            }
        ]
        
        # Save default knowledge base
        kb_file = self.kb_dir / 'farming_knowledge.json'
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump({'documents': self.documents}, f, indent=2)
        
        logger.info("Loaded default knowledge base")
        
        # Build TF-IDF matrix
        doc_texts = [doc.get('content', '') for doc in self.documents]
        self.tfidf_matrix = self.vectorizer.fit_transform(doc_texts)
    
    def search(self, query: str, top_k: int = 3) -> str:
        """Search knowledge base using TF-IDF similarity
        
        Args:
            query: Search query
            top_k: Number of top results
            
        Returns:
            Combined relevant context
        """
        try:
            if not self.documents or self.tfidf_matrix is None:
                logger.warning("Knowledge base is empty")
                return ""
            
            # Vectorize query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Get top K results
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Combine results
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum threshold
                    results.append(self.documents[idx]['content'])
            
            context = " ".join(results)
            logger.info(f"Found {len(results)} relevant documents")
            return context
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return ""
    
    def add_document(self, topic: str, content: str, keywords: list):
        """Add new document to knowledge base
        
        Args:
            topic: Document topic
            content: Document content
            keywords: List of keywords
        """
        try:
            doc_id = max([d.get('id', 0) for d in self.documents]) + 1
            new_doc = {
                "id": doc_id,
                "topic": topic,
                "content": content,
                "keywords": keywords
            }
            self.documents.append(new_doc)
            
            # Rebuild TF-IDF matrix
            doc_texts = [doc.get('content', '') for doc in self.documents]
            self.tfidf_matrix = self.vectorizer.fit_transform(doc_texts)
            
            logger.info(f"Added new document: {topic}")
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
