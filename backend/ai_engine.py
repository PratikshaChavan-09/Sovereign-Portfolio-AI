import os
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import sys

# Debug information (To resolve the Docker issues I was getting on my system please ignore these fallbacks...)
print(f"[AI_ENGINE] Python executable: {sys.executable}")
print(f"[AI_ENGINE] Current working directory: {os.getcwd()}")
print(f"[AI_ENGINE] PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

GENAI_AVAILABLE = False
genai = None
types = None

def try_install_package():
    """Try to install google-generativeai if not available"""
    try:
        import subprocess
        print("[AI_ENGINE] Attempting to install google-generativeai...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--no-cache-dir", "google-generativeai==0.8.4"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("[AI_ENGINE] ✅ google-generativeai installed successfully")
            return True
        else:
            print(f"[AI_ENGINE] ❌ Installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[AI_ENGINE] ❌ Installation error: {e}")
        return False

def import_with_retry():
    """Try importing with multiple strategies"""
    global genai, types, GENAI_AVAILABLE
    
    strategies = [
        # Strategy 1: Direct import
        lambda: __import__('google.generativeai', fromlist=['generativeai']),
        
        # Strategy 2: Try after sys.path modification
        lambda: (
            sys.path.insert(0, '/usr/local/lib/python3.12/site-packages'),
            __import__('google.generativeai', fromlist=['generativeai'])
        )[1],
        
        # Strategy 3: Try after pip install
        lambda: (
            try_install_package(),
            __import__('google.generativeai', fromlist=['generativeai'])
        )[1] if try_install_package() else None
    ]
    
    for i, strategy in enumerate(strategies):
        try:
            print(f"[AI_ENGINE] Trying import strategy {i+1}...")
            genai = strategy()
            if genai:
                print(f"[AI_ENGINE] ✅ Strategy {i+1} successful!")
                
                # Try to import types
                try:
                    from google.genai import types
                    print("[AI_ENGINE] ✅ google.genai.types imported")
                except ImportError:
                    try:
                        types = __import__('google.generativeai.types', fromlist=['types'])
                        print("[AI_ENGINE] ✅ google.generativeai.types imported as fallback")
                    except ImportError:
                        print("[AI_ENGINE] ⚠️ types module not available, using None")
                        types = None
                
                GENAI_AVAILABLE = True
                return True
                
        except Exception as e:
            print(f"[AI_ENGINE] ❌ Strategy {i+1} failed: {e}")
            continue
    
    return False

# Try the import with retry mechanism
try:
    print("[AI_ENGINE] Starting import process...")
    import_success = import_with_retry()
    
    if not import_success:
        print("[AI_ENGINE] ❌ All import strategies failed")
        GENAI_AVAILABLE = False
    
except Exception as e:
    print(f"[AI_ENGINE] ❌ Critical import error: {e}")
    import traceback
    traceback.print_exc()
    GENAI_AVAILABLE = False

# Import other dependencies
try:
    from vector_store import PortfolioVectorStore
except ImportError as e:
    print(f"[AI_ENGINE] ⚠️ vector_store import failed: {e}")
    # Create a dummy vector store
    class DummyVectorStore:
        def add_portfolio_data(self, data): pass
        def get_context_for_query(self, query, data): return ""
        def get_stats(self): return {}
    PortfolioVectorStore = DummyVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioAIEngine:
    """AI Engine for portfolio analysis and recommendations using Gemini LLM"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.client = None
        self.vector_store = PortfolioVectorStore()
        self.chat_history = []
        
        print(f"[AI_ENGINE] Initializing with GENAI_AVAILABLE={GENAI_AVAILABLE}")
        
        # Initialize Gemini client - REQUIRED, no fallbacks
        if not GENAI_AVAILABLE:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set. Please set your Gemini API key.")
        
        try:
            print("[AI_ENGINE] Configuring Gemini client...")
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini AI client initialized successfully")
            
            # Test the client with a simple call
            print("[AI_ENGINE] Testing Gemini client...")
            test_response = self.client.generate_content("Test")
            logger.info(f"Gemini client test successful: {test_response.text}")
            print("[AI_ENGINE] ✅ Gemini client fully operational")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            print(f"[AI_ENGINE] ❌ Gemini client initialization failed: {e}")
            raise RuntimeError(f"Cannot initialize Gemini AI: {str(e)}")
    
    def analyze_portfolio(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive portfolio analysis using AI"""
        try:
            # Add data to vector store for context
            self.vector_store.add_portfolio_data(processed_data)
            
            # Prepare analysis prompt
            portfolio_summary = self._prepare_portfolio_summary(processed_data)
            
            system_instruction = """You are a senior portfolio manager and investment advisor specializing in sovereign fund management. 
            Analyze the provided portfolio data and provide insights on:
            1. Overall portfolio health and performance
            2. Risk assessment and management
            3. Sector allocation and diversification
            4. Performance vs benchmarks
            5. Key strengths and areas for improvement
            
            Be precise, data-driven, and provide actionable insights."""
            
            prompt = f"""Please analyze this sovereign fund portfolio:

{portfolio_summary}

Provide a comprehensive analysis covering performance, risk, diversification, and overall portfolio health."""
            
            analysis = self._generate_content(prompt, system_instruction)
            
            return {
                'analysis': analysis,
                'timestamp': datetime.now().isoformat(),
                'data_summary': portfolio_summary
            }
            
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {str(e)}")
            raise RuntimeError(f"Portfolio analysis failed: {str(e)}")
    
    def generate_recommendations(self, processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered investment recommendations"""
        try:
            portfolio_summary = self._prepare_portfolio_summary(processed_data)
            context = self.vector_store.get_context_for_query("investment recommendations", processed_data)
            
            system_instruction = """You are an expert investment advisor for sovereign wealth funds. 
            Generate specific, actionable investment recommendations based on the portfolio analysis.
            Focus on: optimization opportunities, risk management, diversification improvements, 
            and performance enhancement strategies."""
            
            prompt = f"""Based on this portfolio data and context:

{portfolio_summary}

Context from similar periods:
{context}

Generate 5-7 specific investment recommendations with:
- Clear rationale for each recommendation
- Expected impact on portfolio
- Implementation priority (High/Medium/Low)
- Risk considerations

Format as numbered recommendations."""
            
            recommendations_text = self._generate_content(prompt, system_instruction)
            recommendations = self._parse_recommendations(recommendations_text)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise RuntimeError(f"Recommendation generation failed: {str(e)}")
    
    def chat_with_portfolio(self, user_message: str, processed_data: Dict[str, Any]) -> str:
        """Interactive chat about portfolio data"""
        try:
            # Get relevant context from vector store
            context = self.vector_store.get_context_for_query(user_message, processed_data)
            
            # Add to chat history
            self.chat_history.append({
                'role': 'user',
                'message': user_message,
                'timestamp': datetime.now().isoformat()
            })
            
            system_instruction = """You are a knowledgeable portfolio advisor with access to detailed portfolio data. 
            Answer questions about the portfolio using the specific data provided. Be detailed, specific, and use actual numbers 
            from the data. Do not give generic responses - always reference the actual portfolio holdings, performance metrics, 
            and risk data provided in the context."""
            
            # Build conversation context with recent history
            recent_history = self.chat_history[-5:]  # Last 5 messages
            history_text = "\n".join([f"{msg['role']}: {msg['message']}" for msg in recent_history[-4:]])
            
            # Create comprehensive prompt with all available data
            prompt = f"""COMPLETE PORTFOLIO CONTEXT:
{context}

RECENT CONVERSATION:
{history_text}

CURRENT USER QUESTION: {user_message}

Please provide a detailed, specific answer using the actual portfolio data above. Include specific company names, 
exact percentages, and real numbers from the data. Do not give generic responses."""
            
            # Generate content with Gemini
            logger.info(f"Calling Gemini API for chat query: {user_message[:50]}...")
            response = self._generate_content(prompt, system_instruction)
            logger.info("Gemini API call successful")
            
            # Add response to history
            self.chat_history.append({
                'role': 'assistant',
                'message': response,
                'timestamp': datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise RuntimeError(f"AI chat failed: {str(e)}")
    
    def _generate_content(self, prompt: str, system_instruction: str, temperature: float = 0.3) -> str:
        """Generate content using Gemini API"""
        try:
            # Create full prompt with system instruction
            full_prompt = f"{system_instruction}\n\n{prompt}"
            
            # Handle different generation config approaches
            try:
                if types and hasattr(types, 'GenerationConfig'):
                    generation_config = types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=2000,
                    )
                else:
                    # Fallback for different versions
                    generation_config = {
                        'temperature': temperature,
                        'max_output_tokens': 2000,
                    }
                
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
            except Exception as config_error:
                print(f"[AI_ENGINE] Config error, using basic generation: {config_error}")
                response = self.client.generate_content(full_prompt)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {str(e)}")
            raise
    
    def _prepare_portfolio_summary(self, data: Dict[str, Any]) -> str:
        """Prepare comprehensive portfolio summary for AI analysis"""
        summary_parts = []
        
        # Portfolio overview
        if 'portfolio_summary' in data:
            portfolio = data['portfolio_summary']
            summary_parts.append("PORTFOLIO OVERVIEW:")
            summary_parts.append(f"Fund: {portfolio.get('fund_name', 'Unknown')}")
            summary_parts.append(f"AUM: {portfolio.get('total_aum', 0):,.0f} {portfolio.get('base_currency', 'INR')}")
            summary_parts.append(f"Holdings: {portfolio.get('total_holdings', 0)}")
            summary_parts.append(f"Target Return: {portfolio.get('target_return', 0):.1%}")
            summary_parts.append(f"Risk Level: {portfolio.get('risk_level', 'Unknown')}")
            summary_parts.append("")
        
        # Performance metrics
        if 'performance_summary' in data:
            perf = data['performance_summary']
            summary_parts.append("PERFORMANCE METRICS:")
            summary_parts.append(f"Current Value: {perf.get('current_value', 0):,.0f}")
            summary_parts.append(f"Total Return: {perf.get('total_return', 0):.2%}")
            summary_parts.append(f"Daily Return: {perf.get('daily_return', 0):.2%}")
            summary_parts.append(f"Volatility: {perf.get('volatility', 0):.2%}")
            summary_parts.append(f"Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
            summary_parts.append(f"Max Drawdown: {perf.get('max_drawdown', 0):.2%}")
            summary_parts.append(f"Active Return: {perf.get('active_return', 0):.2%}")
            summary_parts.append("")
        
        # Risk metrics
        if 'risk_summary' in data:
            risk = data['risk_summary']
            summary_parts.append("RISK METRICS:")
            summary_parts.append(f"Portfolio Beta: {risk.get('portfolio_beta', 0):.2f}")
            summary_parts.append(f"VaR (95%): {risk.get('var_95', 0):,.0f}")
            summary_parts.append(f"CVaR (95%): {risk.get('cvar_95', 0):,.0f}")
            summary_parts.append(f"Tracking Error: {risk.get('tracking_error', 0):.3f}")
            summary_parts.append(f"Correlation with Benchmark: {risk.get('correlation_benchmark', 0):.3f}")
            summary_parts.append(f"Concentration Risk: {risk.get('concentration_risk', 0):.3f}")
            summary_parts.append(f"Liquidity Score: {risk.get('liquidity_score', 0):.1f}")
            summary_parts.append("")
        
        # COMPLETE HOLDINGS DATA - Enhanced with all details
        if 'raw_holdings_df' in data and data['raw_holdings_df']:
            holdings_list = data['raw_holdings_df']
            summary_parts.append("COMPLETE HOLDINGS DETAILS:")
            summary_parts.append(f"Total Holdings: {len(holdings_list)}")
            summary_parts.append("All Holdings with Full Details:")
            
            # Sort by market value descending
            sorted_holdings = sorted(holdings_list, key=lambda x: x.get('Market_Value', 0), reverse=True)
            
            for i, holding in enumerate(sorted_holdings):
                summary_parts.append(
                    f"{i+1:2d}. {holding.get('Asset_Name', 'Unknown'):<35} "
                    f"| Ticker: {holding.get('Ticker_Symbol', 'N/A'):<15} "
                    f"| Sector: {holding.get('Sector', 'Unknown'):<20} "
                    f"| Weight: {holding.get('Weight_Percent', 0):>6.2%} "
                    f"| Market Value: ₹{holding.get('Market_Value', 0):>15,.0f} "
                    f"| Price: ₹{holding.get('Current_Price', 0):>8.2f} "
                    f"| ESG: {holding.get('ESG_Rating', 'N/A'):<4} "
                    f"| Dividend: {holding.get('Dividend_Yield', 0):>5.2%}"
                )
            summary_parts.append("")
            
        elif 'top_holdings' in data and data['top_holdings']:
            # Fallback to top holdings if raw data not available
            summary_parts.append("TOP HOLDINGS:")
            summary_parts.append(f"Showing Top {len(data['top_holdings'])} Holdings:")
            for i, holding in enumerate(data['top_holdings']):
                summary_parts.append(
                    f"{i+1:2d}. {holding.get('Asset_Name', 'Unknown'):<30} "
                    f"({holding.get('Ticker_Symbol', 'N/A'):<12}) "
                    f"Sector: {holding.get('Sector', 'Unknown'):<20} "
                    f"Weight: {holding.get('Weight_Percent', 0):.2%} "
                    f"Value: ₹{holding.get('Market_Value', 0):,.0f} "
                    f"ESG: {holding.get('ESG_Rating', 'N/A')}"
                )
            summary_parts.append("")
        
        # SECTOR ALLOCATION - Enhanced
        if 'sector_allocation' in data and data['sector_allocation']:
            summary_parts.append("SECTOR ALLOCATION:")
            total_value = sum(data['sector_allocation'].values())
            sorted_sectors = sorted(data['sector_allocation'].items(), key=lambda x: x[1], reverse=True)
            for sector, value in sorted_sectors:
                weight = value / total_value if total_value > 0 else 0
                summary_parts.append(f"- {sector:<25}: {weight:.1%} ({value:,.0f} INR)")
            summary_parts.append("")
        
        # GEOGRAPHIC ALLOCATION - If available
        if 'holdings_data' in data and 'geographic_allocation' in data['holdings_data']:
            geo_data = data['holdings_data']['geographic_allocation']
            summary_parts.append("GEOGRAPHIC ALLOCATION:")
            for geo, value in geo_data.items():
                summary_parts.append(f"- {geo}: {value}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _parse_recommendations(self, recommendations_text: str) -> List[Dict[str, Any]]:
        """Parse AI-generated recommendations into structured format"""
        recommendations = []
        
        try:
            lines = recommendations_text.split('\n')
            current_rec = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if it's a numbered recommendation
                if line[0].isdigit() and '.' in line[:3]:
                    # Save previous recommendation
                    if current_rec:
                        recommendations.append(current_rec)
                    
                    # Start new recommendation
                    title = line.split('.', 1)[1].strip()
                    current_rec = {
                        'title': title,
                        'description': '',
                        'priority': 'Medium',
                        'rationale': '',
                        'impact': ''
                    }
                elif current_rec:
                    # Add to description
                    if 'priority' in line.lower():
                        if 'high' in line.lower():
                            current_rec['priority'] = 'High'
                        elif 'low' in line.lower():
                            current_rec['priority'] = 'Low'
                    else:
                        current_rec['description'] += ' ' + line
                        current_rec['rationale'] += ' ' + line
            
            # Add last recommendation
            if current_rec:
                recommendations.append(current_rec)
            
            # Clean up descriptions
            for rec in recommendations:
                rec['description'] = rec['description'].strip()
                rec['rationale'] = rec['rationale'].strip()
                if not rec['description']:
                    rec['description'] = rec['title']
                if not rec['rationale']:
                    rec['rationale'] = rec['description']
            
        except Exception as e:
            logger.error(f"Error parsing recommendations: {str(e)}")
            # Return basic parsed version
            lines = [line.strip() for line in recommendations_text.split('\n') if line.strip()]
            for i, line in enumerate(lines[:7]):
                if line:
                    recommendations.append({
                        'title': f"Recommendation {i+1}",
                        'description': line,
                        'priority': 'Medium',
                        'rationale': line,
                        'impact': 'Portfolio optimization'
                    })
        
        return recommendations[:7]  # Limit to 7 recommendations
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get chat history"""
        return self.chat_history
    
    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_history = []
        logger.info("Chat history cleared")
    
    def get_vector_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return self.vector_store.get_stats()
