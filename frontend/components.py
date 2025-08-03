import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
from utils import format_currency, format_percentage

def render_portfolio_overview(portfolio_summary, performance_data, risk_data):
    """Render portfolio overview cards and key metrics"""
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h4>💰 Total AUM</h4>
                <h2>{}</h2>
                <p>{}</p>
            </div>
        """.format(
            format_currency(portfolio_summary.get('total_aum', 0)),
            portfolio_summary.get('base_currency', 'INR')
        ), unsafe_allow_html=True)
    
    with col2:
        total_return = performance_data.get('total_return', 0)
        return_color = "green" if total_return >= 0 else "red"
        st.markdown("""
            <div class="metric-card">
                <h4>📈 Total Return</h4>
                <h2 style="color: {}">{}</h2>
                <p>vs Target: {}</p>
            </div>
        """.format(
            return_color,
            format_percentage(total_return),
            format_percentage(portfolio_summary.get('target_return', 0))
        ), unsafe_allow_html=True)
    
    with col3:
        sharpe_ratio = performance_data.get('sharpe_ratio', 0)
        sharpe_color = "green" if sharpe_ratio > 1 else "orange" if sharpe_ratio > 0.5 else "red"
        st.markdown("""
            <div class="metric-card">
                <h4>⚡ Sharpe Ratio</h4>
                <h2 style="color: {}">{:.2f}</h2>
                <p>Risk-Adj. Return</p>
            </div>
        """.format(sharpe_color, sharpe_ratio), unsafe_allow_html=True)
    
    with col4:
        risk_level = portfolio_summary.get('risk_level', 'Unknown')
        risk_color = {"Low": "green", "Moderate": "orange", "High": "red"}.get(risk_level, "gray")
        st.markdown("""
            <div class="metric-card">
                <h4>⚠️ Risk Level</h4>
                <h2 style="color: {}">{}</h2>
                <p>Beta: {:.2f}</p>
            </div>
        """.format(
            risk_color,
            risk_level,
            risk_data.get('portfolio_beta', 0)
        ), unsafe_allow_html=True)

def render_performance_charts(historical_data, benchmark_data=None, chart_type='overview'):
    """Render performance charts"""
    
    if historical_data.empty:
        st.warning("No historical performance data available")
        return
    
    if chart_type == 'overview':
        # Simple portfolio value chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=historical_data['Date'],
            y=historical_data['Portfolio_Value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=3)
        ))
        
        fig.update_layout(
            title="Portfolio Value Over Time",
            xaxis_title="Date",
            yaxis_title="Portfolio Value (₹)",
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Detailed performance analysis
        
        # Performance vs Benchmark
        col1, col2 = st.columns(2)
        
        with col1:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(
                    x=historical_data['Date'],
                    y=historical_data['Cumulative_Return'] * 100,
                    mode='lines',
                    name='Portfolio Return',
                    line=dict(color='#1f77b4', width=2)
                ),
                secondary_y=False,
            )
            
            if not historical_data['Benchmark_Return'].isna().all():
                fig.add_trace(
                    go.Scatter(
                        x=historical_data['Date'],
                        y=historical_data['Benchmark_Return'] * 100,
                        mode='lines',
                        name='Benchmark Return',
                        line=dict(color='#ff7f0e', width=2, dash='dash')
                    ),
                    secondary_y=False,
                )
            
            fig.update_layout(
                title="Cumulative Returns vs Benchmark",
                height=400
            )
            fig.update_yaxes(title_text="Return (%)", secondary_y=False)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Volatility and Sharpe Ratio
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Rolling Volatility', 'Sharpe Ratio'),
                vertical_spacing=0.1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=historical_data['Date'],
                    y=historical_data['Volatility'] * 100,
                    mode='lines',
                    name='Volatility',
                    line=dict(color='red', width=2)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=historical_data['Date'],
                    y=historical_data['Sharpe_Ratio'],
                    mode='lines',
                    name='Sharpe Ratio',
                    line=dict(color='green', width=2)
                ),
                row=2, col=1
            )
            
            fig.update_layout(height=400, showlegend=False)
            fig.update_yaxes(title_text="Volatility (%)", row=1, col=1)
            fig.update_yaxes(title_text="Sharpe Ratio", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Daily returns distribution
        st.markdown("#### 📊 Daily Returns Distribution")
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=historical_data['Daily_Return'] * 100,
            nbinsx=30,
            name='Daily Returns',
            marker_color='skyblue',
            opacity=0.7
        ))
        
        fig.update_layout(
            title="Distribution of Daily Returns",
            xaxis_title="Daily Return (%)",
            yaxis_title="Frequency",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_holdings_analysis(holdings_data, holdings_df):
    """Render holdings analysis charts and tables"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sector allocation pie chart
        sector_allocation = holdings_data.get('sector_allocation', {})
        if sector_allocation:
            fig = px.pie(
                values=list(sector_allocation.values()),
                names=list(sector_allocation.keys()),
                title="Sector Allocation",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top holdings bar chart
        top_holdings = holdings_data.get('top_holdings', [])[:10]
        if top_holdings:
            holdings_df_viz = pd.DataFrame(top_holdings)
            
            fig = px.bar(
                holdings_df_viz,
                x='Weight_Percent',
                y='Asset_Name',
                orientation='h',
                title="Top 10 Holdings by Weight",
                color='Weight_Percent',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )
            fig.update_traces(texttemplate='%{x:.1%}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
    
    # Holdings detail table
    st.markdown("#### 📋 Holdings Detail")
    
    if not holdings_df.empty:
        # Format the dataframe for display
        display_df = holdings_df.copy()
        display_df = display_df.sort_values('Market_Value', ascending=False)
        
        # Select key columns
        columns_to_show = [
            'Asset_Name', 'Ticker_Symbol', 'Sector', 'Weight_Percent',
            'Market_Value', 'Current_Price', 'ESG_Rating', 'Dividend_Yield'
        ]
        
        display_df = display_df[columns_to_show]
        
        # Format columns
        formatted_df = display_df.style.format({
            'Weight_Percent': '{:.2%}',
            'Market_Value': '₹{:,.0f}',
            'Current_Price': '₹{:.2f}',
            'Dividend_Yield': '{:.2%}'
        })
        
        st.dataframe(formatted_df, use_container_width=True)
    
    # Geographic and ESG analysis
    col1, col2 = st.columns(2)
    
    with col1:
        if not holdings_df.empty:
            # Geographic allocation
            geo_allocation = holdings_df.groupby('Geography')['Market_Value'].sum()
            
            fig = px.pie(
                values=geo_allocation.values,
                names=geo_allocation.index,
                title="Geographic Allocation"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not holdings_df.empty:
            # ESG rating distribution
            esg_counts = holdings_df['ESG_Rating'].value_counts()
            
            fig = px.bar(
                x=esg_counts.index,
                y=esg_counts.values,
                title="ESG Rating Distribution",
                color=esg_counts.values,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

def render_risk_dashboard(risk_data, risk_summary):
    """Render risk analysis dashboard"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # VaR over time
        if not risk_data.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=risk_data['Date'],
                y=risk_data['VaR_95'],
                mode='lines',
                name='VaR 95%',
                line=dict(color='red', width=2),
                fill='tonexty'
            ))
            
            fig.add_trace(go.Scatter(
                x=risk_data['Date'],
                y=risk_data['CVaR_95'],
                mode='lines',
                name='CVaR 95%',
                line=dict(color='darkred', width=2)
            ))
            
            fig.update_layout(
                title="Value at Risk (VaR) Analysis",
                xaxis_title="Date",
                yaxis_title="Risk Value (₹)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Risk metrics gauge
        beta = risk_summary.get('portfolio_beta', 1.0)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = beta,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Portfolio Beta"},
            delta = {'reference': 1.0},
            gauge = {
                'axis': {'range': [None, 2]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.8], 'color': "lightgray"},
                    {'range': [0.8, 1.2], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 1.5
                }
            }
        ))
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk metrics summary table
    if risk_summary:
        st.markdown("#### 📊 Risk Metrics Summary")
        
        risk_metrics = [
            ["Portfolio Beta", f"{risk_summary.get('portfolio_beta', 0):.3f}"],
            ["Value at Risk (95%)", format_currency(risk_summary.get('var_95', 0))],
            ["Conditional VaR (95%)", format_currency(risk_summary.get('cvar_95', 0))],
            ["Tracking Error", f"{risk_summary.get('tracking_error', 0):.3f}"],
            ["Correlation with Benchmark", f"{risk_summary.get('correlation_benchmark', 0):.3f}"],
            ["Concentration Risk", f"{risk_summary.get('concentration_risk', 0):.3f}"],
            ["Liquidity Score", f"{risk_summary.get('liquidity_score', 0):.1f}"]
        ]
        
        risk_df = pd.DataFrame(risk_metrics, columns=['Metric', 'Value'])
        st.dataframe(risk_df, use_container_width=True, hide_index=True)

def render_recommendations_section(recommendations):
    """Render AI recommendations in an organized format"""
    
    if not recommendations or len(recommendations) == 0:
        st.info("🔄 No recommendations generated yet. Try refreshing or check your AI analysis.")
        return
    
    # Priority filter
    col1, col2 = st.columns([3, 1])
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "High", "Medium", "Low"]
        )
    
    # Filter recommendations
    filtered_recs = recommendations
    if priority_filter != "All":
        filtered_recs = [rec for rec in recommendations if rec.get('priority') == priority_filter]
    
    if not filtered_recs:
        st.warning(f"No {priority_filter.lower()} priority recommendations found.")
        return
    
    # Display recommendations
    for i, rec in enumerate(filtered_recs):
        priority = rec.get('priority', 'Medium')
        priority_color = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}.get(priority, 'gray')
        
        with st.expander(f"🎯 {rec.get('title', f'Recommendation {i+1}')}", expanded=(priority == 'High')):
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:**")
                st.write(rec.get('description', 'No description available'))
                
                st.markdown(f"**Rationale:**")
                st.write(rec.get('rationale', 'No rationale provided'))
                
                if rec.get('impact'):
                    st.markdown(f"**Expected Impact:**")
                    st.write(rec.get('impact'))
            
            with col2:
                st.markdown(f"""
                    <div class="priority-badge priority-{priority.lower()}">
                        <h4>Priority</h4>
                        <h3>{priority}</h3>
                    </div>
                """, unsafe_allow_html=True)

def render_chat_interface(ai_engine):
    """Render the chat interface for portfolio Q&A"""
    
    # Get current processed data for context
    processed_data = {
        'portfolio_summary': st.session_state.get('portfolio_summary', {}),
        'holdings_data': st.session_state.get('holdings_data', {}),
        'performance_summary': st.session_state.get('performance_data', {}),
        'risk_summary': st.session_state.get('risk_data', {}),
        'top_holdings': st.session_state.get('holdings_data', {}).get('top_holdings', []),
        'sector_allocation': st.session_state.get('holdings_data', {}).get('sector_allocation', {}),
        'raw_holdings_df': st.session_state.get('data_processor').get_raw_data('Holdings_Detail').to_dict('records') if 'data_processor' in st.session_state else []
    }
    
    # Initialize chat messages if not exists
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input (outside any containers)
    if prompt := st.chat_input("Ask me anything about your portfolio..."):
        # Add user message to history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Analyzing your portfolio..."):
                try:
                    
                    # Debug: Show what data is being sent
                    st.write("🔍 **Debug**: Processing your question with complete portfolio data...")
                    
                    # Call the AI engine with complete data
                    response = ai_engine.chat_with_portfolio(prompt, processed_data)
                    
                    # Check if we got a meaningful response (not fallback)
                    if "I can provide information about portfolio performance" in response:
                        st.warning("⚠️ **Fallback Response Detected** - AI engine not working properly")
                        st.write("**Raw Response:**", response)
                        
                        # Try to force a proper AI call
                        st.write("🔄 **Attempting direct AI analysis...**")
                        
                        # Create a detailed prompt with data
                        detailed_prompt = f"""
                        PORTFOLIO DATA CONTEXT:
                        {ai_engine.vector_store.get_context_for_query(prompt, processed_data)}
                        
                        USER QUESTION: {prompt}
                        
                        Please provide a detailed, specific answer about this portfolio using the data provided above.
                        """
                        
                        # Try direct AI generation
                        try:
                            if hasattr(ai_engine, '_generate_content'):
                                response = ai_engine._generate_content(
                                    detailed_prompt,
                                    "You are a portfolio advisor. Answer questions using the specific portfolio data provided."
                                )
                                st.write("✅ **Enhanced AI Response:**")
                                st.write(response)
                            else:
                                st.error("AI engine method not available")
                        except Exception as e:
                            st.error(f"Direct AI call failed: {str(e)}")
                    else:
                        st.write(response)
                    
                    # Add assistant response to history
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_response = f"❌ Error generating response: {str(e)}"
                    st.error(error_response)
                    st.exception(e)  # Show full traceback
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_response})
    
    # Chat controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Clear Chat History"):
            st.session_state.chat_messages = []
            if hasattr(ai_engine, 'clear_chat_history'):
                ai_engine.clear_chat_history()
            st.rerun()
        
    # Suggested questions
    with st.expander("💡 Suggested Questions"):
        suggestions = [
            "What are the key risks in my portfolio?",
            "How is my portfolio performing vs benchmark?", 
            "Which sectors should I consider reducing?",
            "What are my top performing holdings?",
            "How can I improve diversification?",
            "Explain my portfolio in detail with specific numbers",
            "What is my current ESG exposure?"
        ]
        
        for suggestion in suggestions:
            if st.button(suggestion, key=f"suggest_{hash(suggestion)}"):
                # Add suggestion as user message
                st.session_state.chat_messages.append({"role": "user", "content": suggestion})
                
                # Generate AI response
                try:
                    response = ai_engine.chat_with_portfolio(suggestion, processed_data)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception as e:
                    error_response = f"I apologize, but I encountered an error: {str(e)}"
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_response})
                    st.rerun()