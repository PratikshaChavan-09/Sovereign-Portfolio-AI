import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any, Dict, List

def initialize_session_state():
    """Initialize session state variables"""
    
    # Data storage
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'raw_data' not in st.session_state:
        st.session_state.raw_data = {}
    
    if 'portfolio_summary' not in st.session_state:
        st.session_state.portfolio_summary = {}
    
    if 'holdings_data' not in st.session_state:
        st.session_state.holdings_data = {}
    
    if 'performance_data' not in st.session_state:
        st.session_state.performance_data = {}
    
    if 'risk_data' not in st.session_state:
        st.session_state.risk_data = {}
    
    # AI components
    if 'ai_analysis' not in st.session_state:
        st.session_state.ai_analysis = {}
    
    if 'ai_recommendations' not in st.session_state:
        st.session_state.ai_recommendations = []
    
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Processing control
    if 'last_processed_file' not in st.session_state:
        st.session_state.last_processed_file = None
        
    if 'ai_analysis_done' not in st.session_state:
        st.session_state.ai_analysis_done = False
    
    # API keys
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ''

def load_custom_css():
    """Load custom CSS for styling"""
    
    st.markdown("""
        <style>
        /* Main header styling */
        .main-header {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .main-header p {
            margin: 0.5rem 0 0 0;
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        /* Metric cards */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #1e3c72;
            margin-bottom: 1rem;
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
        
        .metric-card h4 {
            margin: 0 0 0.5rem 0;
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            font-weight: 600;
        }
        
        .metric-card h2 {
            margin: 0 0 0.5rem 0;
            color: #1e3c72;
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        .metric-card p {
            margin: 0;
            color: #888;
            font-size: 0.8rem;
        }
        
        /* Welcome container */
        .welcome-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem;
            border-radius: 15px;
            text-align: center;
            margin: 2rem 0;
        }
        
        .welcome-container h2 {
            margin-bottom: 1rem;
            font-size: 2rem;
        }
        
        .welcome-container h3 {
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #f0f0f0;
        }
        
        .welcome-container ul {
            text-align: left;
            margin: 1rem 0;
        }
        
        .welcome-container li {
            margin: 0.5rem 0;
            padding-left: 0.5rem;
        }
        
        /* Priority badges */
        .priority-badge {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .priority-high {
            border-left: 4px solid #e74c3c;
        }
        
        .priority-medium {
            border-left: 4px solid #f39c12;
        }
        
        .priority-low {
            border-left: 4px solid #27ae60;
        }
        
        .priority-badge h4 {
            margin: 0 0 0.5rem 0;
            color: #666;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        
        .priority-badge h3 {
            margin: 0;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        /* Chat styling */
        .stChatMessage {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        
        /* Success/Warning/Error alerts */
        .stSuccess, .stInfo {
            border-radius: 8px;
            border: none;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .stWarning {
            background-color: #fff3cd;
            color: #856404;
            border-radius: 8px;
        }
        
        .stError {
            background-color: #f8d7da;
            color: #721c24;
            border-radius: 8px;
        }
        
        /* DataFrame styling */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 6px;
            border: none;
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Plotly chart container */
        .js-plotly-plot {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0px 0px;
            background-color: #f8f9fa;
            color: #666;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            color: white;
        }
        
        /* File uploader */
        .stFileUploader {
            border-radius: 8px;
            border: 2px dashed #ddd;
            padding: 1rem;
        }
        
        /* Hide streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        </style>
    """, unsafe_allow_html=True)

def format_currency(amount: float, currency: str = "₹") -> str:
    """Format currency values with appropriate scaling"""
    
    if pd.isna(amount) or amount == 0:
        return f"{currency}0"
    
    abs_amount = abs(amount)
    
    if abs_amount >= 1e12:  # Trillion
        return f"{currency}{amount/1e12:.2f}T"
    elif abs_amount >= 1e9:  # Billion
        return f"{currency}{amount/1e9:.2f}B"
    elif abs_amount >= 1e6:  # Million
        return f"{currency}{amount/1e6:.2f}M"
    elif abs_amount >= 1e3:  # Thousand
        return f"{currency}{amount/1e3:.2f}K"
    else:
        return f"{currency}{amount:,.2f}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage values"""
    
    if pd.isna(value):
        return "N/A"
    
    return f"{value * 100:.{decimals}f}%"

def format_number(value: float, decimals: int = 2) -> str:
    """Format numerical values with comma separators"""
    
    if pd.isna(value):
        return "N/A"
    
    return f"{value:,.{decimals}f}"

def calculate_portfolio_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate additional portfolio metrics"""
    
    metrics = {}
    
    # Performance metrics
    if 'performance_summary' in data:
        perf = data['performance_summary']
        
        # Risk-adjusted metrics
        total_return = perf.get('total_return', 0)
        volatility = perf.get('volatility', 0)
        
        if volatility > 0:
            metrics['return_volatility_ratio'] = total_return / volatility
        else:
            metrics['return_volatility_ratio'] = 0
        
        # Drawdown analysis
        max_drawdown = perf.get('max_drawdown', 0)
        if max_drawdown < 0:
            metrics['recovery_factor'] = total_return / abs(max_drawdown)
        else:
            metrics['recovery_factor'] = float('inf')
    
    # Holdings concentration
    if 'holdings_data' in data:
        holdings = data['holdings_data']
        top_holdings = holdings.get('top_holdings', [])
        
        if top_holdings:
            # Top 5 concentration
            top_5_weights = sum([h.get('Weight_Percent', 0) for h in top_holdings[:5]])
            metrics['top_5_concentration'] = top_5_weights
            
            # Top 10 concentration
            top_10_weights = sum([h.get('Weight_Percent', 0) for h in top_holdings[:10]])
            metrics['top_10_concentration'] = top_10_weights
            
            # Herfindahl index for sector concentration
            sector_allocation = holdings.get('sector_allocation', {})
            if sector_allocation:
                total_value = sum(sector_allocation.values())
                if total_value > 0:
                    herfindahl = sum((value / total_value) ** 2 for value in sector_allocation.values())
                    metrics['sector_herfindahl'] = herfindahl
    
    return metrics

def create_performance_summary(data: Dict[str, Any]) -> str:
    """Create a text summary of portfolio performance"""
    
    summary_parts = []
    
    if 'portfolio_summary' in data:
        portfolio = data['portfolio_summary']
        summary_parts.append(f"Portfolio: {portfolio.get('fund_name', 'Unknown Fund')}")
        summary_parts.append(f"AUM: {format_currency(portfolio.get('total_aum', 0))}")
    
    if 'performance_summary' in data:
        perf = data['performance_summary']
        summary_parts.append(f"Total Return: {format_percentage(perf.get('total_return', 0))}")
        summary_parts.append(f"Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
        summary_parts.append(f"Max Drawdown: {format_percentage(perf.get('max_drawdown', 0))}")
    
    if 'risk_summary' in data:
        risk = data['risk_summary']
        summary_parts.append(f"Portfolio Beta: {risk.get('portfolio_beta', 0):.2f}")
        summary_parts.append(f"VaR (95%): {format_currency(risk.get('var_95', 0))}")
    
    return " | ".join(summary_parts)

def validate_data_completeness(data: Dict[str, Any]) -> Dict[str, bool]:
    """Validate completeness of portfolio data"""
    
    validation = {
        'portfolio_overview': bool(data.get('portfolio_summary')),
        'holdings_data': bool(data.get('holdings_data', {}).get('top_holdings')),
        'performance_data': bool(data.get('performance_summary')),
        'risk_data': bool(data.get('risk_summary')),
        'historical_data': len(data.get('historical_performance', [])) > 0
    }
    
    return validation

def generate_alerts(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate portfolio alerts based on data analysis"""
    
    alerts = []
    
    # Performance alerts
    if 'performance_summary' in data:
        perf = data['performance_summary']
        
        total_return = perf.get('total_return', 0)
        if total_return < -0.05:  # -5% return
            alerts.append({
                'type': 'warning',
                'title': 'Poor Performance',
                'message': f'Portfolio showing negative return of {format_percentage(total_return)}'
            })
        
        sharpe_ratio = perf.get('sharpe_ratio', 0)
        if sharpe_ratio < 0.5:
            alerts.append({
                'type': 'warning',
                'title': 'Low Risk-Adjusted Returns',
                'message': f'Sharpe ratio of {sharpe_ratio:.2f} indicates poor risk-adjusted performance'
            })
    
    # Risk alerts
    if 'risk_summary' in data:
        risk = data['risk_summary']
        
        concentration_risk = risk.get('concentration_risk', 0)
        if concentration_risk > 0.4:
            alerts.append({
                'type': 'error',
                'title': 'High Concentration Risk',
                'message': f'Concentration risk of {concentration_risk:.1%} exceeds recommended levels'
            })
        
        var_95 = risk.get('var_95', 0)
        if var_95 < -50000000:  # -50M threshold
            alerts.append({
                'type': 'warning',
                'title': 'High Value at Risk',
                'message': f'VaR (95%) of {format_currency(var_95)} indicates high potential losses'
            })
    
    # Holdings alerts
    if 'holdings_data' in data:
        holdings = data['holdings_data']
        total_holdings = holdings.get('total_holdings', 0)
        
        if total_holdings < 10:
            alerts.append({
                'type': 'info',
                'title': 'Limited Diversification',
                'message': f'Only {total_holdings} holdings may limit diversification benefits'
            })
    
    return alerts

def export_portfolio_report(data: Dict[str, Any]) -> str:
    """Generate a formatted portfolio report for export"""
    
    report_lines = []
    
    # Header
    report_lines.append("SOVEREIGN FUND PORTFOLIO REPORT")
    report_lines.append("=" * 50)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Portfolio summary
    if 'portfolio_summary' in data:
        portfolio = data['portfolio_summary']
        report_lines.append("PORTFOLIO OVERVIEW")
        report_lines.append("-" * 20)
        report_lines.append(f"Fund Name: {portfolio.get('fund_name', 'Unknown')}")
        report_lines.append(f"Total AUM: {format_currency(portfolio.get('total_aum', 0))}")
        report_lines.append(f"Base Currency: {portfolio.get('base_currency', 'Unknown')}")
        report_lines.append(f"Risk Level: {portfolio.get('risk_level', 'Unknown')}")
        report_lines.append(f"Target Return: {format_percentage(portfolio.get('target_return', 0))}")
        report_lines.append("")
    
    # Performance summary
    if 'performance_summary' in data:
        perf = data['performance_summary']
        report_lines.append("PERFORMANCE METRICS")
        report_lines.append("-" * 20)
        report_lines.append(f"Total Return: {format_percentage(perf.get('total_return', 0))}")
        report_lines.append(f"Daily Return: {format_percentage(perf.get('daily_return', 0))}")
        report_lines.append(f"Volatility: {format_percentage(perf.get('volatility', 0))}")
        report_lines.append(f"Sharpe Ratio: {perf.get('sharpe_ratio', 0):.2f}")
        report_lines.append(f"Max Drawdown: {format_percentage(perf.get('max_drawdown', 0))}")
        report_lines.append("")
    
    # Risk summary
    if 'risk_summary' in data:
        risk = data['risk_summary']
        report_lines.append("RISK METRICS")
        report_lines.append("-" * 20)
        report_lines.append(f"Portfolio Beta: {risk.get('portfolio_beta', 0):.3f}")
        report_lines.append(f"VaR (95%): {format_currency(risk.get('var_95', 0))}")
        report_lines.append(f"Tracking Error: {risk.get('tracking_error', 0):.3f}")
        report_lines.append(f"Concentration Risk: {format_percentage(risk.get('concentration_risk', 0))}")
        report_lines.append("")
    
    # Top holdings
    if 'holdings_data' in data:
        holdings = data['holdings_data']
        top_holdings = holdings.get('top_holdings', [])[:10]
        
        if top_holdings:
            report_lines.append("TOP 10 HOLDINGS")
            report_lines.append("-" * 20)
            for i, holding in enumerate(top_holdings, 1):
                report_lines.append(
                    f"{i:2d}. {holding.get('Asset_Name', 'Unknown'):<30} "
                    f"{format_percentage(holding.get('Weight_Percent', 0)):>8} "
                    f"{format_currency(holding.get('Market_Value', 0)):>12}"
                )
            report_lines.append("")
    
    return "\n".join(report_lines)