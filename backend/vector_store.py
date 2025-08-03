import faiss
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
import pickle
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioVectorStore:
    """FAISS-based vector store for portfolio data and context retrieval"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = None
        self.embeddings = []
        self.metadata = []
        self.is_trained = False
        
        # Initialize FAISS index (CPU)
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
        
    def _create_embeddings(self, data: Dict[str, Any]) -> np.ndarray:
        """Create embeddings from portfolio data"""
        try:
            # Extract numerical features for embedding
            features = []
            
            # Portfolio level features
            if 'portfolio_summary' in data:
                portfolio = data['portfolio_summary']
                features.extend([
                    float(portfolio.get('total_aum', 0)) / 1e9,  # Normalized AUM
                    float(portfolio.get('target_return', 0)),
                    float(portfolio.get('total_holdings', 0)) / 100,  # Normalized holdings count
                ])
            
            # Performance features
            if 'performance_summary' in data:
                perf = data['performance_summary']
                features.extend([
                    float(perf.get('total_return', 0)),
                    float(perf.get('daily_return', 0)),
                    float(perf.get('volatility', 0)),
                    float(perf.get('sharpe_ratio', 0)),
                    float(perf.get('max_drawdown', 0)),
                    float(perf.get('active_return', 0))
                ])
            
            # Risk features
            if 'risk_summary' in data:
                risk = data['risk_summary']
                features.extend([
                    float(risk.get('portfolio_beta', 0)),
                    float(risk.get('var_95', 0)) / 1e6,  # Normalized VaR
                    float(risk.get('tracking_error', 0)),
                    float(risk.get('correlation_benchmark', 0)),
                    float(risk.get('concentration_risk', 0)),
                    float(risk.get('liquidity_score', 0)) / 10
                ])
            
            # Sector diversification features
            if 'sector_allocation' in data:
                sectors = data['sector_allocation']
                total_value = sum(sectors.values()) if sectors else 1
                # Top 5 sectors by weight
                sector_weights = sorted(sectors.values(), reverse=True)[:5] if sectors else [0] * 5
                normalized_weights = [w / total_value for w in sector_weights]
                features.extend(normalized_weights)
                
                # Sector concentration (Herfindahl index)
                herfindahl = sum((w / total_value) ** 2 for w in sectors.values()) if sectors else 0
                features.append(herfindahl)
            
            # Pad or truncate to fixed dimension
            while len(features) < self.dimension:
                features.append(0.0)
            features = features[:self.dimension]
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            return np.zeros(self.dimension, dtype=np.float32)
    
    def add_portfolio_data(self, processed_data: Dict[str, Any], timestamp: str = None) -> int:
        """Add portfolio data to vector store"""
        try:
            # Create embedding
            embedding = self._create_embeddings(processed_data)
            
            # Create metadata
            metadata = {
                'timestamp': timestamp or datetime.now().isoformat(),
                'data_summary': self._create_data_summary(processed_data),
                'portfolio_name': processed_data.get('portfolio_summary', {}).get('fund_name', 'Unknown'),
                'total_return': processed_data.get('performance_summary', {}).get('total_return', 0),
                'volatility': processed_data.get('performance_summary', {}).get('volatility', 0),
                'risk_level': processed_data.get('portfolio_summary', {}).get('risk_level', 'Unknown')
            }
            
            # Add to index
            embedding_reshaped = embedding.reshape(1, -1)
            self.index.add(embedding_reshaped)
            
            # Store metadata
            vector_id = len(self.embeddings)
            self.embeddings.append(embedding)
            self.metadata.append(metadata)
            
            self.is_trained = True
            logger.info(f"Added portfolio data with ID: {vector_id}")
            
            return vector_id
            
        except Exception as e:
            logger.error(f"Error adding portfolio data: {str(e)}")
            raise
    
    def _create_data_summary(self, data: Dict[str, Any]) -> str:
        """Create text summary of portfolio data"""
        summary_parts = []
        
        if 'portfolio_summary' in data:
            portfolio = data['portfolio_summary']
            summary_parts.append(f"Portfolio: {portfolio.get('fund_name', 'Unknown')}")
            summary_parts.append(f"AUM: {portfolio.get('total_aum', 0):,.0f}")
            summary_parts.append(f"Risk Level: {portfolio.get('risk_level', 'Unknown')}")
        
        if 'performance_summary' in data:
            perf = data['performance_summary']
            summary_parts.append(f"Return: {perf.get('total_return', 0):.2%}")
            summary_parts.append(f"Volatility: {perf.get('volatility', 0):.2%}")
            summary_parts.append(f"Sharpe: {perf.get('sharpe_ratio', 0):.2f}")
        
        if 'risk_summary' in data:
            risk = data['risk_summary']
            summary_parts.append(f"Beta: {risk.get('portfolio_beta', 0):.2f}")
            summary_parts.append(f"VaR: {risk.get('var_95', 0):,.0f}")
        
        return " | ".join(summary_parts)
    
    def search_similar_portfolios(self, query_data: Dict[str, Any], k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar portfolio states"""
        try:
            if not self.is_trained or len(self.embeddings) == 0:
                return []
            
            # Create query embedding
            query_embedding = self._create_embeddings(query_data)
            query_reshaped = query_embedding.reshape(1, -1)
            
            # Search
            scores, indices = self.index.search(query_reshaped, min(k, len(self.embeddings)))
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.metadata):
                    result = {
                        'similarity_score': float(score),
                        'metadata': self.metadata[idx],
                        'rank': i + 1
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar portfolios: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str, current_data: Dict[str, Any]) -> str:
        """Get relevant context for AI query"""
        try:
            # Search for similar portfolios
            similar_portfolios = self.search_similar_portfolios(current_data, k=2)
            
            context_parts = []
            
            # Add current portfolio summary
            if 'portfolio_summary' in current_data:
                context_parts.append("CURRENT PORTFOLIO:")
                context_parts.append(self._create_data_summary(current_data))
            
            # Add similar historical data
            if similar_portfolios:
                context_parts.append("\nSIMILAR HISTORICAL PERIODS:")
                for result in similar_portfolios:
                    metadata = result['metadata']
                    context_parts.append(f"- {metadata['data_summary']} (Similarity: {result['similarity_score']:.3f})")
            
            # Add query-specific context
            query_lower = query.lower()
            if 'risk' in query_lower:
                if 'risk_summary' in current_data:
                    risk = current_data['risk_summary']
                    context_parts.append(f"\nRISK CONTEXT:")
                    context_parts.append(f"Beta: {risk.get('portfolio_beta', 0):.2f}, VaR: {risk.get('var_95', 0):,.0f}")
                    context_parts.append(f"Tracking Error: {risk.get('tracking_error', 0):.3f}")
            
            elif 'performance' in query_lower or 'return' in query_lower:
                if 'performance_summary' in current_data:
                    perf = current_data['performance_summary']
                    context_parts.append(f"\nPERFORMANCE CONTEXT:")
                    context_parts.append(f"Total Return: {perf.get('total_return', 0):.2%}")
                    context_parts.append(f"Volatility: {perf.get('volatility', 0):.2%}")
                    context_parts.append(f"Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
            
            elif 'holding' in query_lower or 'sector' in query_lower:
                if 'top_holdings' in current_data:
                    context_parts.append(f"\nHOLDINGS CONTEXT:")
                    for holding in current_data['top_holdings'][:3]:
                        context_parts.append(f"- {holding['Asset_Name']}: {holding['Weight_Percent']:.1%}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return "Current portfolio data available for analysis."
    
    def save_index(self, filepath: str):
        """Save FAISS index and metadata"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, f"{filepath}.index")
            
            # Save metadata
            with open(f"{filepath}.metadata", 'wb') as f:
                pickle.dump({
                    'embeddings': self.embeddings,
                    'metadata': self.metadata,
                    'dimension': self.dimension,
                    'is_trained': self.is_trained
                }, f)
            
            logger.info(f"Saved vector store to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise
    
    def load_index(self, filepath: str):
        """Load FAISS index and metadata"""
        try:
            if os.path.exists(f"{filepath}.index"):
                # Load FAISS index
                self.index = faiss.read_index(f"{filepath}.index")
                
                # Load metadata
                with open(f"{filepath}.metadata", 'rb') as f:
                    data = pickle.load(f)
                    self.embeddings = data['embeddings']
                    self.metadata = data['metadata']
                    self.dimension = data['dimension']
                    self.is_trained = data['is_trained']
                
                logger.info(f"Loaded vector store from {filepath}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_vectors': len(self.embeddings),
            'dimension': self.dimension,
            'is_trained': self.is_trained,
            'index_size': self.index.ntotal if self.index else 0
        }