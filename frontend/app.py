import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Add backend to path - go up one level from frontend to root, then into backend
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(os.path.dirname(current_dir), 'backend')
sys.path.insert(0, backend_path)
from dotenv import load_dotenv

load_dotenv()

# Now import from backend
from data_processor import PortfolioDataProcessor
from ai_engine import PortfolioAIEngine

# Import from current frontend directory
from components import (
    render_portfolio_overview, render_performance_charts, 
    render_holdings_analysis, render_risk_dashboard,
    render_recommendations_section, render_chat_interface
)
from utils import (
    initialize_session_state, load_custom_css,
    format_currency, format_percentage
)

# Page config
st.set_page_config(
    page_title="Sovereign Fund Portfolio Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Load custom CSS
    load_custom_css()
    
    # Header
    st.title("🏛️ Sovereign Fund Portfolio Manager")
    st.markdown("*AI-Powered Investment Analysis & Optimization Platform*")
    
    # Sidebar for file upload and settings
    with st.sidebar:
        st.markdown("### 📁 Data Upload")
        
        uploaded_file = st.file_uploader(
            "Upload Portfolio Excel File",
            type=['xlsx', 'xls'],
            help="Upload your sovereign fund portfolio data (Excel format)"
        )
        
        if uploaded_file is not None:
            process_uploaded_file(uploaded_file)
        
        # AI Status
        st.markdown("### 🤖 AI Status")
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            st.success("✅ Gemini API configured")
        else:
            st.error("❌ GEMINI_API_KEY not set in environment")
            st.info("Set environment variable: GEMINI_API_KEY=your_key")
        
        # Manual AI Analysis Trigger
        if st.session_state.get('data_loaded', False) and api_key:
            if st.button("🤖 Generate AI Analysis", help="Manually trigger AI analysis"):
                st.session_state.ai_analysis_done = False
                trigger_ai_analysis()
        
        # Data status
        if 'data_loaded' in st.session_state and st.session_state.data_loaded:
            st.success("✅ Portfolio data loaded")
            st.info(f"📊 {st.session_state.portfolio_summary.get('total_holdings', 0)} holdings")
            st.info(f"💰 {format_currency(st.session_state.portfolio_summary.get('total_aum', 0))}")
            
            # AI Status
            if st.session_state.get('ai_analysis_done', False):
                st.success("✅ AI analysis completed")
            elif api_key:
                st.warning("⏳ AI analysis pending")
            else:
                st.info("🔑 Set GEMINI_API_KEY environment variable")
            
            # Add reset button
            if st.button("🔄 Reset Data", help="Clear all data and start fresh"):
                # Clear all session state data
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            st.warning("⚠️ Please upload portfolio data")
    
    # Main content area
    if 'data_loaded' in st.session_state and st.session_state.data_loaded:
        display_dashboard()
        
        # Show chat interface outside tabs if data is loaded and API key exists
        api_key = os.getenv('GEMINI_API_KEY')
        if st.session_state.get('data_loaded', False) and api_key:
            
            st.markdown("---")
            st.markdown("### 💬 Portfolio Chat Assistant")
            
            # Initialize AI engine if not exists
            if 'ai_engine' not in st.session_state:
                try:
                    st.session_state.ai_engine = PortfolioAIEngine(api_key=api_key)
                except Exception as e:
                    st.error(f"❌ Failed to initialize AI engine: {str(e)}")
                    st.stop()
            
            render_chat_interface(st.session_state.ai_engine)
        elif st.session_state.get('data_loaded', False):
            st.markdown("---")
            st.warning("🔑 Set GEMINI_API_KEY environment variable to enable chat")
    else:
        display_welcome_screen()

def trigger_ai_analysis():
    """Trigger AI analysis manually"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("❌ GEMINI_API_KEY environment variable not set")
            return
            
        if not st.session_state.get('data_loaded', False):
            st.error("❌ Please upload portfolio data first")
            return
            
        with st.spinner("🤖 Generating AI analysis and recommendations..."):
            # Initialize AI engine
            if 'ai_engine' not in st.session_state:
                try:
                    st.session_state.ai_engine = PortfolioAIEngine(api_key=api_key)
                except Exception as e:
                    st.error(f"❌ Failed to initialize AI engine: {str(e)}")
                    return
            
            # Prepare COMPLETE data for AI including raw holdings
            processed_data = {
                'portfolio_summary': st.session_state.portfolio_summary,
                'holdings_data': st.session_state.holdings_data,
                'performance_summary': st.session_state.performance_data,
                'risk_summary': st.session_state.risk_data,
                'top_holdings': st.session_state.holdings_data.get('top_holdings', []),
                'sector_allocation': st.session_state.holdings_data.get('sector_allocation', {}),
                # Add raw holdings dataframe data
                'raw_holdings_df': st.session_state.data_processor.get_raw_data('Holdings_Detail').to_dict('records') if 'data_processor' in st.session_state else []
            }
            
            # Generate analysis and recommendations
            st.session_state.ai_analysis = st.session_state.ai_engine.analyze_portfolio(processed_data)
            st.session_state.ai_recommendations = st.session_state.ai_engine.generate_recommendations(processed_data)
            st.session_state.ai_analysis_done = True
            
            st.success("✅ AI analysis completed successfully!")
            
    except Exception as e:
        st.error(f"❌ Error generating AI analysis: {str(e)}")
        st.exception(e)  # Show full traceback for debugging

def process_uploaded_file(uploaded_file):
    """Process the uploaded Excel file"""
    
    # Check if this file was already processed
    file_hash = str(hash(uploaded_file.name + str(uploaded_file.size)))
    
    if st.session_state.get('last_processed_file') == file_hash and st.session_state.get('data_loaded', False):
        return  # Skip processing if same file already loaded
    
    try:
        with st.spinner("🔄 Processing portfolio data..."):
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Initialize data processor
            if 'data_processor' not in st.session_state:
                st.session_state.data_processor = PortfolioDataProcessor()
            
            # Load and process data
            data = st.session_state.data_processor.load_excel_file(temp_path)
            
            # Store processed data in session state
            st.session_state.raw_data = data
            st.session_state.portfolio_summary = st.session_state.data_processor.get_portfolio_summary()
            st.session_state.holdings_data = st.session_state.data_processor.get_holdings_data()
            st.session_state.performance_data = st.session_state.data_processor.get_performance_data()
            st.session_state.risk_data = st.session_state.data_processor.get_risk_data()
            st.session_state.data_loaded = True
            st.session_state.last_processed_file = file_hash
            st.session_state.ai_analysis_done = False  # Reset AI analysis flag
            
            # Clean up temp file
            os.remove(temp_path)
            
            st.success("✅ Portfolio data loaded successfully!")
            
            # Automatically trigger AI analysis if API key is available
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                trigger_ai_analysis()
            
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.exception(e)  # Show full traceback for debugging

def display_welcome_screen():
    """Display welcome screen when no data is loaded"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🎯 Welcome to Portfolio Manager")
        st.markdown("Upload your sovereign fund portfolio Excel file to get started with AI-powered analysis.")
        
        st.markdown("### 📋 Expected File Format:")
        st.markdown("""
        - **Portfolio_Overview** - Fund information and metadata
        - **Holdings_Detail** - Individual asset holdings
        - **Historical_Performance** - Time series performance data
        - **Benchmarks** - Market benchmark data
        - **Risk_Metrics** - Risk assessment metrics
        - **Cash_Flows** - Transaction history
        - **Market_Data** - External market indicators
        """)
        
        st.markdown("### 🚀 Features:")
        st.markdown("""
        - 📊 Interactive portfolio dashboard
        - 🤖 AI-powered investment recommendations
        - 💬 Chat with your portfolio data
        - 📈 Performance and risk analytics
        - 🎯 Optimization suggestions
        """)

def display_dashboard():
    """Display the main portfolio dashboard"""
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", 
        "📈 Performance", 
        "🎯 Holdings", 
        "🤖 AI Recommendations"
    ])
    
    with tab1:
        display_overview_dashboard()
    
    with tab2:
        display_performance_section()
    
    with tab3:
        display_holdings_section()
    
    with tab4:
        display_recommendations_section()

def display_overview_dashboard():
    """Display the main overview dashboard"""
    
    # Portfolio overview cards
    render_portfolio_overview(
        st.session_state.portfolio_summary,
        st.session_state.performance_data,
        st.session_state.risk_data
    )
    
    st.markdown("---")
    
    # Key metrics row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Quick Performance Snapshot")
        render_performance_charts(
            st.session_state.data_processor.get_time_series_data(
                'Historical_Performance', 
                ['Portfolio_Value', 'Cumulative_Return']
            ),
            chart_type='overview'
        )
    
    with col2:
        st.markdown("### 🎯 Top Holdings")
        top_holdings = st.session_state.holdings_data.get('top_holdings', [])[:5]
        if top_holdings:
            holdings_df = pd.DataFrame(top_holdings)
            st.dataframe(
                holdings_df[['Asset_Name', 'Weight_Percent', 'Market_Value']].style.format({
                    'Weight_Percent': '{:.2%}',
                    'Market_Value': '₹{:,.0f}'
                }),
                use_container_width=True,
                hide_index=True
            )

def display_performance_section():
    """Display detailed performance analytics"""
    
    st.markdown("### 📈 Performance Analytics")
    
    # Performance charts
    render_performance_charts(
        st.session_state.data_processor.get_time_series_data('Historical_Performance'),
        st.session_state.data_processor.get_time_series_data('Benchmarks'),
        chart_type='detailed'
    )
    
    # Risk dashboard
    st.markdown("### ⚠️ Risk Analysis")
    render_risk_dashboard(
        st.session_state.data_processor.get_time_series_data('Risk_Metrics'),
        st.session_state.risk_data
    )

def display_holdings_section():
    """Display holdings analysis"""
    
    st.markdown("### 🎯 Holdings Analysis")
    
    render_holdings_analysis(
        st.session_state.holdings_data,
        st.session_state.data_processor.get_raw_data('Holdings_Detail')
    )

def display_recommendations_section():
    """Display AI recommendations"""
    
    st.markdown("### 🤖 AI Investment Recommendations")
    
    if 'ai_recommendations' in st.session_state:
        render_recommendations_section(st.session_state.ai_recommendations)
    else:
        st.info("🔑 Please provide Gemini API key in the sidebar to enable AI recommendations")
    
    # AI Analysis
    if 'ai_analysis' in st.session_state:
        st.markdown("### 📋 Portfolio Analysis")
        with st.expander("View AI Analysis", expanded=True):
            st.markdown(st.session_state.ai_analysis.get('analysis', 'No analysis available'))

if __name__ == "__main__":
    main()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 20px;'>"
        "Made with ❤️ by Pratiksha Chavan"
        "</div>", 
        unsafe_allow_html=True
    )
